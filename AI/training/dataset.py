"""
Dataset classes for training
"""
import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path


class ConversationDataset(Dataset):
    """
    Dataset for conversation examples
    Used for SFT training
    """
    
    def __init__(
        self,
        data_path: str,
        tokenizer,
        max_length: int = 2048,
        prompt_template: str = None
    ):
        """
        Args:
            data_path: Path to JSONL file with examples
            tokenizer: Tokenizer
            max_length: Maximum sequence length
            prompt_template: Template for formatting prompts
        """
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prompt_template = prompt_template or "{instruction}\n\n{input}\n\nОтвет: {output}"
        
        # Load data
        self.examples = []
        self._load_data(data_path)
    
    def _load_data(self, data_path: str):
        """Load data from file"""
        if not os.path.exists(data_path):
            print(f"Data file not found: {data_path}")
            return
        
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    example = json.loads(line.strip())
                    self.examples.append(example)
                except json.JSONDecodeError:
                    continue
        
        print(f"Loaded {len(self.examples)} examples from {data_path}")
    
    def _format_example(self, example: Dict) -> str:
        """Format example into text"""
        instruction = example.get("instruction", "")
        input_text = example.get("input", "")
        output = example.get("output", "")
        
        # Use template
        text = self.prompt_template.format(
            instruction=instruction,
            input=input_text,
            output=output
        )
        
        return text
    
    def __len__(self) -> int:
        return len(self.examples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        example = self.examples[idx]
        text = self._format_example(example)
        
        # Tokenize
        encoded = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        input_ids = encoded["input_ids"].squeeze(0)
        attention_mask = encoded["attention_mask"].squeeze(0)
        
        # Labels are same as input_ids for language modeling
        labels = input_ids.clone()
        
        # Mask padding in labels
        labels[labels == self.tokenizer.pad_token_id] = -100
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }


class PreferenceDataset(Dataset):
    """
    Dataset for preference learning (DPO)
    Each example has a prompt, chosen response, and rejected response
    """
    
    def __init__(
        self,
        data_path: str,
        tokenizer,
        max_length: int = 2048
    ):
        """
        Args:
            data_path: Path to JSONL file with preference examples
            tokenizer: Tokenizer
            max_length: Maximum sequence length
        """
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        self.examples = []
        self._load_data(data_path)
    
    def _load_data(self, data_path: str):
        """Load preference data"""
        if not os.path.exists(data_path):
            print(f"Data file not found: {data_path}")
            return
        
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    example = json.loads(line.strip())
                    # Validate structure
                    if all(k in example for k in ["prompt", "chosen", "rejected"]):
                        self.examples.append(example)
                except json.JSONDecodeError:
                    continue
        
        print(f"Loaded {len(self.examples)} preference examples from {data_path}")
    
    def __len__(self) -> int:
        return len(self.examples)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        example = self.examples[idx]
        
        prompt = example["prompt"]
        chosen = example["chosen"]
        rejected = example["rejected"]
        
        # Format full sequences
        chosen_text = f"{prompt}\n\nОтвет: {chosen}"
        rejected_text = f"{prompt}\n\nОтвет: {rejected}"
        
        # Tokenize chosen
        chosen_encoded = self.tokenizer(
            chosen_text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Tokenize rejected
        rejected_encoded = self.tokenizer(
            rejected_text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "chosen_input_ids": chosen_encoded["input_ids"].squeeze(0),
            "chosen_attention_mask": chosen_encoded["attention_mask"].squeeze(0),
            "chosen_labels": chosen_encoded["input_ids"].squeeze(0),
            "rejected_input_ids": rejected_encoded["input_ids"].squeeze(0),
            "rejected_attention_mask": rejected_encoded["attention_mask"].squeeze(0),
            "rejected_labels": rejected_encoded["input_ids"].squeeze(0)
        }


def create_sample_data(output_dir: str = "./data"):
    """Create sample training data files"""
    os.makedirs(output_dir, exist_ok=True)
    
    # SFT examples
    sft_examples = [
        {
            "instruction": "Помоги подготовиться к сложному разговору с начальником о повышении зарплаты",
            "input": "Я работаю в компании 2 года, выполняю больше обязанностей, чем предусмотрено, но зарплата не менялась.",
            "output": """План подготовки к разговору о повышении зарплаты:

1. **Подготовка фактов**
   - Составьте список ваших достижений за 2 года
   - Соберите примеры дополнительных обязанностей
   - Узнайте рыночную зарплату для вашей позиции

2. **Структура разговора**
   - Начните с позитива: "Мне нравится работать в компании..."
   - Перейдите к фактам: "За это время я взял на себя..."
   - Сформулируйте просьбу: "Я хотел бы обсудить пересмотр компенсации"

3. **Ключевые фразы**
   - "Я ценю возможности, которые даёт компания"
   - "Мой вклад в проекты X, Y, Z показывает..."
   - "Считаю справедливым обсудить корректировку зарплаты"

4. **Работа с возражениями**
   - "Сейчас не лучшее время" → "Когда было бы удобно вернуться к этому вопросу?"
   - "Бюджет ограничен" → "Возможны ли другие формы компенсации?"

Удачи в разговоре!"""
        },
        {
            "instruction": "Проанализируй эту переписку и дай рекомендации",
            "input": "Ты вечно всё делаешь не так! Почему ты никогда не слушаешь, что я говорю?",
            "output": """Анализ сообщения:

**Выявленные проблемы:**
1. ❌ Обобщения ("вечно", "никогда") - усиливают конфликт
2. ❌ "Ты-сообщения" - воспринимаются как обвинения
3. ❌ Риторические вопросы - не ведут к решению

**Рекомендации:**

Вместо: "Ты вечно всё делаешь не так!"
Лучше: "Мне важно, чтобы это было сделано определённым образом. Давай обсудим детали?"

Вместо: "Почему ты никогда не слушаешь?"
Лучше: "Я чувствую, что меня не услышали. Можем ли мы вместе разобрать, что произошло?"

**Техники для улучшения:**
- Используйте Я-сообщения: "Я расстроен", а не "Ты меня расстроил"
- Избегайте абсолютных слов: замените "никогда" на "в этот раз"
- Формулируйте конкретные просьбы вместо претензий"""
        }
    ]
    
    # Save SFT data
    sft_path = os.path.join(output_dir, "train", "sft_data.jsonl")
    os.makedirs(os.path.dirname(sft_path), exist_ok=True)
    
    with open(sft_path, "w", encoding="utf-8") as f:
        for example in sft_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    # DPO preference examples
    preference_examples = [
        {
            "prompt": "Как ответить коллеге, который постоянно перебивает на совещаниях?",
            "chosen": "Попробуйте мягко, но уверенно сказать: 'Позволь мне закончить мысль, потом с удовольствием выслушаю тебя.' Важно сохранять спокойный тон и зрительный контакт. Если ситуация повторяется, можно обсудить это наедине: 'Заметил, что мы часто перебиваем друг друга. Давай договоримся дослушивать до конца?'",
            "rejected": "Просто игнорируйте его или перебивайте в ответ. Можете также пожаловаться начальству."
        },
        {
            "prompt": "Как отказать другу в просьбе одолжить деньги?",
            "chosen": "Отказывать близким сложно, но важно быть честным. Можно сказать: 'Я ценю, что ты обратился ко мне, но сейчас я не могу одолжить эту сумму. Могу помочь подумать над другими вариантами решения.' Не нужно оправдываться или врать - достаточно уважительного, но твёрдого отказа.",
            "rejected": "Скажите, что у вас нет денег, даже если это неправда. Или просто не отвечайте на сообщения."
        }
    ]
    
    # Save preference data
    pref_path = os.path.join(output_dir, "train", "preference_data.jsonl")
    
    with open(pref_path, "w", encoding="utf-8") as f:
        for example in preference_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    print(f"Sample data created in {output_dir}")
    print(f"  SFT examples: {len(sft_examples)}")
    print(f"  Preference examples: {len(preference_examples)}")
    
    return sft_path, pref_path
