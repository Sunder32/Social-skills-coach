"""
Social Skills Model - Custom PyTorch model for communication coaching
"""
import torch
import torch.nn as nn
from torch.nn import functional as F
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
import os
import json

from config import config


@dataclass
class ModelOutput:
    """Model output container"""
    logits: torch.Tensor
    loss: Optional[torch.Tensor] = None
    hidden_states: Optional[Tuple[torch.Tensor]] = None
    attentions: Optional[Tuple[torch.Tensor]] = None


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism"""
    
    def __init__(self, hidden_size: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert hidden_size % num_heads == 0
        
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        
        self.q_proj = nn.Linear(hidden_size, hidden_size)
        self.k_proj = nn.Linear(hidden_size, hidden_size)
        self.v_proj = nn.Linear(hidden_size, hidden_size)
        self.out_proj = nn.Linear(hidden_size, hidden_size)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = self.head_dim ** -0.5
    
    def forward(
        self, 
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        output_attentions: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        batch_size, seq_len, _ = hidden_states.shape
        
        # Project Q, K, V
        q = self.q_proj(hidden_states)
        k = self.k_proj(hidden_states)
        v = self.v_proj(hidden_states)
        
        # Reshape for multi-head attention
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Compute attention scores
        attn_weights = torch.matmul(q, k.transpose(-2, -1)) * self.scale
        
        # Apply causal mask
        causal_mask = torch.triu(
            torch.ones(seq_len, seq_len, device=hidden_states.device), 
            diagonal=1
        ).bool()
        attn_weights = attn_weights.masked_fill(causal_mask, float('-inf'))
        
        # Apply attention mask if provided
        if attention_mask is not None:
            attn_weights = attn_weights + attention_mask
        
        attn_weights = F.softmax(attn_weights, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Compute output
        attn_output = torch.matmul(attn_weights, v)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_size)
        attn_output = self.out_proj(attn_output)
        
        if output_attentions:
            return attn_output, attn_weights
        return attn_output, None


class FeedForward(nn.Module):
    """Feed-forward network with GELU activation"""
    
    def __init__(self, hidden_size: int, intermediate_size: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(hidden_size, intermediate_size)
        self.fc2 = nn.Linear(intermediate_size, hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.fc2(hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states


class TransformerBlock(nn.Module):
    """Single transformer block"""
    
    def __init__(self, hidden_size: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(hidden_size, num_heads, dropout)
        self.feed_forward = FeedForward(hidden_size, hidden_size * 4, dropout)
        self.ln1 = nn.LayerNorm(hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        output_attentions: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        # Self-attention with residual
        residual = hidden_states
        hidden_states = self.ln1(hidden_states)
        attn_output, attn_weights = self.attention(
            hidden_states, attention_mask, output_attentions
        )
        hidden_states = residual + attn_output
        
        # Feed-forward with residual
        residual = hidden_states
        hidden_states = self.ln2(hidden_states)
        hidden_states = residual + self.feed_forward(hidden_states)
        
        return hidden_states, attn_weights


class SocialSkillsModel(nn.Module):
    """
    Custom transformer model for social skills coaching
    Optimized for Russian language and communication scenarios
    """
    
    def __init__(
        self,
        vocab_size: int = 50257,
        hidden_size: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        max_length: int = 2048,
        dropout: float = 0.1,
        pad_token_id: int = 0
    ):
        super().__init__()
        
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.max_length = max_length
        self.pad_token_id = pad_token_id
        
        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, hidden_size, padding_idx=pad_token_id)
        self.position_embedding = nn.Embedding(max_length, hidden_size)
        self.embedding_dropout = nn.Dropout(dropout)
        
        # Transformer blocks
        self.layers = nn.ModuleList([
            TransformerBlock(hidden_size, num_heads, dropout)
            for _ in range(num_layers)
        ])
        
        # Output
        self.ln_final = nn.LayerNorm(hidden_size)
        self.lm_head = nn.Linear(hidden_size, vocab_size, bias=False)
        
        # Tie weights
        self.lm_head.weight = self.token_embedding.weight
        
        # Initialize weights
        self.apply(self._init_weights)
        
        # Config for saving
        self.config = {
            "vocab_size": vocab_size,
            "hidden_size": hidden_size,
            "num_layers": num_layers,
            "num_heads": num_heads,
            "max_length": max_length,
            "dropout": dropout,
            "pad_token_id": pad_token_id
        }
    
    def _init_weights(self, module):
        """Initialize weights"""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False
    ) -> ModelOutput:
        batch_size, seq_len = input_ids.shape
        device = input_ids.device
        
        # Create position ids
        position_ids = torch.arange(seq_len, device=device).unsqueeze(0).expand(batch_size, -1)
        
        # Embeddings
        token_embeds = self.token_embedding(input_ids)
        position_embeds = self.position_embedding(position_ids)
        hidden_states = self.embedding_dropout(token_embeds + position_embeds)
        
        # Process attention mask
        if attention_mask is not None:
            attention_mask = attention_mask[:, None, None, :]
            attention_mask = (1.0 - attention_mask) * -10000.0
        
        # Transformer layers
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        
        for layer in self.layers:
            if output_hidden_states:
                all_hidden_states += (hidden_states,)
            
            hidden_states, attn_weights = layer(
                hidden_states, attention_mask, output_attentions
            )
            
            if output_attentions:
                all_attentions += (attn_weights,)
        
        # Final layer norm
        hidden_states = self.ln_final(hidden_states)
        
        if output_hidden_states:
            all_hidden_states += (hidden_states,)
        
        # Language model head
        logits = self.lm_head(hidden_states)
        
        # Compute loss if labels provided
        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss = F.cross_entropy(
                shift_logits.view(-1, self.vocab_size),
                shift_labels.view(-1),
                ignore_index=self.pad_token_id
            )
        
        return ModelOutput(
            logits=logits,
            loss=loss,
            hidden_states=all_hidden_states,
            attentions=all_attentions
        )
    
    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
        eos_token_id: Optional[int] = None,
        pad_token_id: Optional[int] = None
    ) -> torch.Tensor:
        """Generate text autoregressively"""
        
        self.eval()
        device = input_ids.device
        
        for _ in range(max_new_tokens):
            # Truncate if needed
            idx_cond = input_ids if input_ids.size(1) <= self.max_length else input_ids[:, -self.max_length:]
            
            # Forward pass
            outputs = self(idx_cond)
            logits = outputs.logits[:, -1, :]
            
            # Apply repetition penalty
            if repetition_penalty != 1.0:
                for i in range(input_ids.size(0)):
                    for token_id in set(input_ids[i].tolist()):
                        logits[i, token_id] /= repetition_penalty
            
            # Apply temperature
            logits = logits / temperature
            
            # Apply top-k filtering
            if top_k > 0:
                indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                logits[indices_to_remove] = float('-inf')
            
            # Apply top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                
                indices_to_remove = sorted_indices_to_remove.scatter(
                    1, sorted_indices, sorted_indices_to_remove
                )
                logits[indices_to_remove] = float('-inf')
            
            # Sample
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            # Append
            input_ids = torch.cat([input_ids, next_token], dim=1)
            
            # Check for EOS
            if eos_token_id is not None and (next_token == eos_token_id).all():
                break
        
        return input_ids
    
    def save_pretrained(self, save_path: str):
        """Save model and config"""
        os.makedirs(save_path, exist_ok=True)
        
        # Save model weights
        torch.save(self.state_dict(), os.path.join(save_path, "pytorch_model.bin"))
        
        # Save config
        with open(os.path.join(save_path, "config.json"), "w") as f:
            json.dump(self.config, f, indent=2)
        
        print(f"Model saved to {save_path}")
    
    @classmethod
    def from_pretrained(cls, load_path: str, device: str = "cpu") -> "SocialSkillsModel":
        """Load model from path"""
        # Load config
        config_path = os.path.join(load_path, "config.json")
        with open(config_path, "r") as f:
            model_config = json.load(f)
        
        # Create model
        model = cls(**model_config)
        
        # Load weights
        weights_path = os.path.join(load_path, "pytorch_model.bin")
        state_dict = torch.load(weights_path, map_location=device)
        model.load_state_dict(state_dict)
        
        model.to(device)
        print(f"Model loaded from {load_path}")
        
        return model
    
    def get_num_params(self) -> int:
        """Get number of parameters"""
        return sum(p.numel() for p in self.parameters())
    
    def get_num_trainable_params(self) -> int:
        """Get number of trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
