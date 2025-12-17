"""
SFT Trainer - Supervised Fine-Tuning for Social Skills Model
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import get_linear_schedule_with_warmup
from typing import Optional, Dict, Any, Callable
import os
import json
from datetime import datetime
from tqdm import tqdm

from config import config
from core.model import SocialSkillsModel
from training.dataset import ConversationDataset


class SFTTrainer:
    """
    Supervised Fine-Tuning Trainer
    Trains the model on conversation examples
    """
    
    def __init__(
        self,
        model: SocialSkillsModel,
        tokenizer,
        train_dataset: ConversationDataset,
        eval_dataset: Optional[ConversationDataset] = None,
        output_dir: str = None,
        callbacks: list = None
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.output_dir = output_dir or config.training.checkpoint_dir
        self.callbacks = callbacks or []
        
        self.device = config.training.device if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Training state
        self.global_step = 0
        self.epoch = 0
        self.best_eval_loss = float('inf')
        self.training_history = []
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def train(
        self,
        num_epochs: int = None,
        batch_size: int = None,
        learning_rate: float = None,
        warmup_steps: int = None,
        gradient_accumulation_steps: int = None,
        max_grad_norm: float = None,
        save_steps: int = None,
        eval_steps: int = None,
        logging_steps: int = None,
        fp16: bool = None,
        progress_callback: Callable = None
    ) -> Dict[str, Any]:
        """
        Run training loop
        
        Args:
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            warmup_steps: Number of warmup steps
            gradient_accumulation_steps: Gradient accumulation steps
            max_grad_norm: Maximum gradient norm for clipping
            save_steps: Save checkpoint every N steps
            eval_steps: Evaluate every N steps
            logging_steps: Log metrics every N steps
            fp16: Use mixed precision training
            progress_callback: Callback function(step, total, metrics)
            
        Returns:
            Training history
        """
        # Use config defaults if not specified
        num_epochs = num_epochs or config.training.num_epochs
        batch_size = batch_size or config.training.batch_size
        learning_rate = learning_rate or config.training.learning_rate
        warmup_steps = warmup_steps or config.training.warmup_steps
        gradient_accumulation_steps = gradient_accumulation_steps or config.training.gradient_accumulation_steps
        max_grad_norm = max_grad_norm or config.training.max_grad_norm
        save_steps = save_steps or config.training.save_steps
        eval_steps = eval_steps or config.training.eval_steps
        logging_steps = logging_steps or config.training.logging_steps
        fp16 = fp16 if fp16 is not None else config.training.fp16
        
        # Create data loader
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True
        )
        
        # Optimizer
        optimizer = AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=config.training.weight_decay
        )
        
        # Scheduler
        total_steps = len(train_loader) * num_epochs // gradient_accumulation_steps
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        # Mixed precision
        scaler = torch.cuda.amp.GradScaler() if fp16 and self.device == "cuda" else None
        
        # Training loop
        self.model.train()
        accumulated_loss = 0
        
        print(f"\n{'='*50}")
        print(f"Starting training")
        print(f"  Epochs: {num_epochs}")
        print(f"  Batch size: {batch_size}")
        print(f"  Learning rate: {learning_rate}")
        print(f"  Total steps: {total_steps}")
        print(f"  Device: {self.device}")
        print(f"{'='*50}\n")
        
        for epoch in range(num_epochs):
            self.epoch = epoch
            epoch_loss = 0
            epoch_steps = 0
            
            progress_bar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}")
            
            for step, batch in enumerate(progress_bar):
                # Move batch to device
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                # Forward pass
                if scaler:
                    with torch.cuda.amp.autocast():
                        outputs = self.model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            labels=labels
                        )
                        loss = outputs.loss / gradient_accumulation_steps
                    
                    scaler.scale(loss).backward()
                else:
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    loss = outputs.loss / gradient_accumulation_steps
                    loss.backward()
                
                accumulated_loss += loss.item()
                epoch_loss += loss.item() * gradient_accumulation_steps
                epoch_steps += 1
                
                # Gradient accumulation
                if (step + 1) % gradient_accumulation_steps == 0:
                    # Clip gradients
                    if scaler:
                        scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_grad_norm)
                    
                    # Optimizer step
                    if scaler:
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        optimizer.step()
                    
                    scheduler.step()
                    optimizer.zero_grad()
                    
                    self.global_step += 1
                    
                    # Logging
                    if self.global_step % logging_steps == 0:
                        avg_loss = accumulated_loss / logging_steps
                        lr = scheduler.get_last_lr()[0]
                        
                        metrics = {
                            "step": self.global_step,
                            "loss": avg_loss,
                            "lr": lr,
                            "epoch": epoch + step / len(train_loader)
                        }
                        
                        self.training_history.append(metrics)
                        progress_bar.set_postfix(loss=f"{avg_loss:.4f}", lr=f"{lr:.2e}")
                        
                        if progress_callback:
                            progress_callback(self.global_step, total_steps, metrics)
                        
                        accumulated_loss = 0
                    
                    # Evaluation
                    if self.eval_dataset and self.global_step % eval_steps == 0:
                        eval_loss = self.evaluate()
                        
                        if eval_loss < self.best_eval_loss:
                            self.best_eval_loss = eval_loss
                            self.save_checkpoint("best")
                        
                        self.model.train()
                    
                    # Save checkpoint
                    if self.global_step % save_steps == 0:
                        self.save_checkpoint(f"step_{self.global_step}")
            
            # End of epoch
            avg_epoch_loss = epoch_loss / epoch_steps
            print(f"\nEpoch {epoch + 1} completed. Average loss: {avg_epoch_loss:.4f}")
            
            # Save epoch checkpoint
            self.save_checkpoint(f"epoch_{epoch + 1}")
        
        # Save final model
        self.save_checkpoint("final")
        self.model.save_pretrained(os.path.join(self.output_dir, "final_model"))
        self.tokenizer.save_pretrained(os.path.join(self.output_dir, "final_model"))
        
        print("\n Training completed!")
        return {"history": self.training_history}
    
    def evaluate(self) -> float:
        """Evaluate model on eval dataset"""
        if self.eval_dataset is None:
            return float('inf')
        
        self.model.eval()
        
        eval_loader = DataLoader(
            self.eval_dataset,
            batch_size=config.training.batch_size,
            shuffle=False
        )
        
        total_loss = 0
        total_steps = 0
        
        with torch.no_grad():
            for batch in eval_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                total_loss += outputs.loss.item()
                total_steps += 1
        
        avg_loss = total_loss / total_steps
        print(f"\nEval loss: {avg_loss:.4f}")
        
        return avg_loss
    
    def save_checkpoint(self, name: str):
        """Save training checkpoint"""
        checkpoint_path = os.path.join(self.output_dir, f"checkpoint_{name}")
        os.makedirs(checkpoint_path, exist_ok=True)
        
        # Save model
        torch.save(
            self.model.state_dict(),
            os.path.join(checkpoint_path, "pytorch_model.bin")
        )
        
        # Save training state
        state = {
            "global_step": self.global_step,
            "epoch": self.epoch,
            "best_eval_loss": self.best_eval_loss,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(os.path.join(checkpoint_path, "training_state.json"), "w") as f:
            json.dump(state, f, indent=2)
        
        print(f"Checkpoint saved: {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load training checkpoint"""
        # Load model weights
        state_dict = torch.load(
            os.path.join(checkpoint_path, "pytorch_model.bin"),
            map_location=self.device
        )
        self.model.load_state_dict(state_dict)
        
        # Load training state
        state_path = os.path.join(checkpoint_path, "training_state.json")
        if os.path.exists(state_path):
            with open(state_path, "r") as f:
                state = json.load(f)
            
            self.global_step = state.get("global_step", 0)
            self.epoch = state.get("epoch", 0)
            self.best_eval_loss = state.get("best_eval_loss", float('inf'))
        
        print(f"Checkpoint loaded: {checkpoint_path}")
