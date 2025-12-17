"""
DPO Trainer - Direct Preference Optimization
For training model with human preferences
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from typing import Optional, Dict, Any, Tuple
import os
import json
from datetime import datetime
from tqdm import tqdm

from config import config
from core.model import SocialSkillsModel


class DPOTrainer:
    """
    Direct Preference Optimization Trainer
    Trains the model to prefer better responses over worse ones
    """
    
    def __init__(
        self,
        model: SocialSkillsModel,
        ref_model: SocialSkillsModel,
        tokenizer,
        train_dataset,
        eval_dataset=None,
        output_dir: str = None,
        beta: float = None
    ):
        """
        Args:
            model: Model to train
            ref_model: Reference model (frozen)
            tokenizer: Tokenizer
            train_dataset: Dataset with (prompt, chosen, rejected) examples
            eval_dataset: Evaluation dataset
            output_dir: Output directory
            beta: DPO beta parameter (controls KL divergence penalty)
        """
        self.model = model
        self.ref_model = ref_model
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.output_dir = output_dir or config.training.checkpoint_dir
        self.beta = beta or config.training.dpo_beta
        
        self.device = config.training.device if torch.cuda.is_available() else "cpu"
        
        # Move models to device
        self.model.to(self.device)
        self.ref_model.to(self.device)
        
        # Freeze reference model
        self.ref_model.eval()
        for param in self.ref_model.parameters():
            param.requires_grad = False
        
        # Training state
        self.global_step = 0
        self.training_history = []
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def compute_dpo_loss(
        self,
        policy_chosen_logps: torch.Tensor,
        policy_rejected_logps: torch.Tensor,
        reference_chosen_logps: torch.Tensor,
        reference_rejected_logps: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Compute DPO loss
        
        Args:
            policy_chosen_logps: Log probs of chosen responses from policy model
            policy_rejected_logps: Log probs of rejected responses from policy model
            reference_chosen_logps: Log probs of chosen responses from reference model
            reference_rejected_logps: Log probs of rejected responses from reference model
            
        Returns:
            loss, chosen_rewards, rejected_rewards
        """
        # Compute log ratios
        policy_logratios = policy_chosen_logps - policy_rejected_logps
        reference_logratios = reference_chosen_logps - reference_rejected_logps
        
        # DPO loss
        logits = policy_logratios - reference_logratios
        losses = -F.logsigmoid(self.beta * logits)
        
        # Rewards for logging
        chosen_rewards = self.beta * (policy_chosen_logps - reference_chosen_logps)
        rejected_rewards = self.beta * (policy_rejected_logps - reference_rejected_logps)
        
        return losses.mean(), chosen_rewards.mean(), rejected_rewards.mean()
    
    def get_batch_logps(
        self,
        model: SocialSkillsModel,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor
    ) -> torch.Tensor:
        """Get log probabilities for a batch"""
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        logits = outputs.logits
        
        # Shift for next token prediction
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        
        # Compute log probs
        log_probs = F.log_softmax(shift_logits, dim=-1)
        
        # Gather log probs for actual tokens
        per_token_logps = torch.gather(
            log_probs,
            dim=2,
            index=shift_labels.unsqueeze(2)
        ).squeeze(2)
        
        # Mask padding
        mask = (shift_labels != self.tokenizer.pad_token_id).float()
        
        # Sum log probs (mean over sequence)
        return (per_token_logps * mask).sum(-1) / mask.sum(-1)
    
    def train(
        self,
        num_epochs: int = 1,
        batch_size: int = None,
        learning_rate: float = None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """Run DPO training"""
        
        batch_size = batch_size or config.training.batch_size
        learning_rate = learning_rate or config.training.learning_rate
        
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True
        )
        
        optimizer = AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=config.training.weight_decay
        )
        
        total_steps = len(train_loader) * num_epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=config.training.warmup_steps,
            num_training_steps=total_steps
        )
        
        print(f"\n{'='*50}")
        print(f"Starting DPO Training")
        print(f"  Beta: {self.beta}")
        print(f"  Epochs: {num_epochs}")
        print(f"  Batch size: {batch_size}")
        print(f"{'='*50}\n")
        
        self.model.train()
        
        for epoch in range(num_epochs):
            epoch_loss = 0
            epoch_chosen_rewards = 0
            epoch_rejected_rewards = 0
            
            progress_bar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}")
            
            for step, batch in enumerate(progress_bar):
                # Move to device
                chosen_ids = batch["chosen_input_ids"].to(self.device)
                chosen_mask = batch["chosen_attention_mask"].to(self.device)
                chosen_labels = batch["chosen_labels"].to(self.device)
                
                rejected_ids = batch["rejected_input_ids"].to(self.device)
                rejected_mask = batch["rejected_attention_mask"].to(self.device)
                rejected_labels = batch["rejected_labels"].to(self.device)
                
                # Get policy log probs
                policy_chosen_logps = self.get_batch_logps(
                    self.model, chosen_ids, chosen_mask, chosen_labels
                )
                policy_rejected_logps = self.get_batch_logps(
                    self.model, rejected_ids, rejected_mask, rejected_labels
                )
                
                # Get reference log probs
                with torch.no_grad():
                    ref_chosen_logps = self.get_batch_logps(
                        self.ref_model, chosen_ids, chosen_mask, chosen_labels
                    )
                    ref_rejected_logps = self.get_batch_logps(
                        self.ref_model, rejected_ids, rejected_mask, rejected_labels
                    )
                
                # Compute loss
                loss, chosen_rewards, rejected_rewards = self.compute_dpo_loss(
                    policy_chosen_logps,
                    policy_rejected_logps,
                    ref_chosen_logps,
                    ref_rejected_logps
                )
                
                # Backward
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    config.training.max_grad_norm
                )
                optimizer.step()
                scheduler.step()
                
                self.global_step += 1
                epoch_loss += loss.item()
                epoch_chosen_rewards += chosen_rewards.item()
                epoch_rejected_rewards += rejected_rewards.item()
                
                # Update progress
                progress_bar.set_postfix(
                    loss=f"{loss.item():.4f}",
                    chosen=f"{chosen_rewards.item():.2f}",
                    rejected=f"{rejected_rewards.item():.2f}"
                )
                
                if progress_callback:
                    progress_callback(self.global_step, total_steps, {
                        "loss": loss.item(),
                        "chosen_rewards": chosen_rewards.item(),
                        "rejected_rewards": rejected_rewards.item()
                    })
            
            # Epoch summary
            n_steps = len(train_loader)
            print(f"\nEpoch {epoch + 1} - Loss: {epoch_loss/n_steps:.4f}, "
                  f"Chosen: {epoch_chosen_rewards/n_steps:.2f}, "
                  f"Rejected: {epoch_rejected_rewards/n_steps:.2f}")
            
            self.training_history.append({
                "epoch": epoch + 1,
                "loss": epoch_loss / n_steps,
                "chosen_rewards": epoch_chosen_rewards / n_steps,
                "rejected_rewards": epoch_rejected_rewards / n_steps
            })
        
        # Save final model
        save_path = os.path.join(self.output_dir, "dpo_model")
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        print(f"\nDPO Training completed! Model saved to {save_path}")
        
        return {"history": self.training_history}
