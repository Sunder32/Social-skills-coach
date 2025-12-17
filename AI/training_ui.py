"""
Gradio Training Interface
Web UI for training and managing the Social Skills Model
"""
import gradio as gr
import torch
import os
import json
import threading
from datetime import datetime
from typing import Optional
import traceback

# Import training components
from config import config
from core.model import SocialSkillsModel
from core.llm_client import LLMClient
from training.trainer import SFTTrainer
from training.dpo_trainer import DPOTrainer
from training.dataset import ConversationDataset, PreferenceDataset, create_sample_data


# Global state
training_state = {
    "is_training": False,
    "progress": 0,
    "current_step": 0,
    "total_steps": 0,
    "loss": 0,
    "status": "Готов к обучению",
    "logs": []
}

model = None
tokenizer = None


def log_message(message: str):
    """Add message to logs"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    training_state["logs"].append(f"[{timestamp}] {message}")
    # Keep only last 100 logs
    training_state["logs"] = training_state["logs"][-100:]


def get_model_info():
    """Get information about current model"""
    global model
    
    model_path = config.model.model_path
    
    info = {
        "Статус модели": "Не загружена",
        "Путь": model_path,
        "Параметры": "-",
        "Устройство": config.training.device,
        "GPU доступен": torch.cuda.is_available()
    }
    
    if os.path.exists(model_path):
        info["Статус модели"] = "Сохранена на диске"
        
        config_path = os.path.join(model_path, "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                model_config = json.load(f)
            info["Hidden size"] = model_config.get("hidden_size", "-")
            info["Layers"] = model_config.get("num_layers", "-")
            info["Heads"] = model_config.get("num_heads", "-")
    
    if model is not None:
        info["Статус модели"] = "Загружена в память"
        info["Параметры"] = f"{model.get_num_params():,}"
        info["Trainable"] = f"{model.get_num_trainable_params():,}"
    
    return "\n".join([f"**{k}:** {v}" for k, v in info.items()])


def load_model_handler():
    """Load model into memory"""
    global model, tokenizer
    
    try:
        from transformers import AutoTokenizer
        
        log_message("Загрузка модели...")
        
        model_path = config.model.model_path
        
        if os.path.exists(model_path):
            model = SocialSkillsModel.from_pretrained(
                model_path, 
                device=config.training.device if torch.cuda.is_available() else "cpu"
            )
            tokenizer = AutoTokenizer.from_pretrained(config.model.tokenizer_path)
        else:
            log_message("Модель не найдена, создаём новую...")
            model = SocialSkillsModel(
                vocab_size=config.model.vocab_size,
                hidden_size=config.model.hidden_size,
                num_layers=config.model.num_layers,
                num_heads=config.model.num_heads,
                max_length=config.model.max_length
            )
            
            device = config.training.device if torch.cuda.is_available() else "cpu"
            model.to(device)
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained("ai-forever/rugpt3small_based_on_gpt2")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
        
        log_message(f"Модель загружена! Параметров: {model.get_num_params():,}")
        return get_model_info(), "\n".join(training_state["logs"])
    
    except Exception as e:
        log_message(f"Ошибка загрузки: {str(e)}")
        return get_model_info(), "\n".join(training_state["logs"])


def create_sample_data_handler():
    """Create sample training data"""
    try:
        sft_path, pref_path = create_sample_data(config.data_dir)
        log_message(f"Созданы примеры данных:")
        log_message(f"  SFT: {sft_path}")
        log_message(f"  DPO: {pref_path}")
        return "\n".join(training_state["logs"])
    except Exception as e:
        log_message(f"Ошибка создания данных: {str(e)}")
        return "\n".join(training_state["logs"])


def progress_callback(step, total, metrics):
    """Update training progress"""
    training_state["current_step"] = step
    training_state["total_steps"] = total
    training_state["progress"] = int(step / total * 100) if total > 0 else 0
    training_state["loss"] = metrics.get("loss", 0)


def train_sft_handler(
    data_path: str,
    num_epochs: int,
    batch_size: int,
    learning_rate: float,
    warmup_steps: int
):
    """Start SFT training"""
    global model, tokenizer
    
    if training_state["is_training"]:
        return "Обучение уже запущено!", "\n".join(training_state["logs"]), get_model_info()
    
    if model is None:
        return "Сначала загрузите модель!", "\n".join(training_state["logs"]), get_model_info()
    
    if not os.path.exists(data_path):
        return f"Файл данных не найден: {data_path}", "\n".join(training_state["logs"]), get_model_info()
    
    def train_thread():
        try:
            training_state["is_training"] = True
            training_state["status"] = "Обучение SFT..."
            log_message("Начало SFT обучения")
            
            # Create dataset
            dataset = ConversationDataset(
                data_path=data_path,
                tokenizer=tokenizer,
                max_length=config.model.max_length
            )
            
            if len(dataset) == 0:
                log_message("Ошибка: датасет пуст!")
                training_state["is_training"] = False
                return
            
            log_message(f"Загружено {len(dataset)} примеров")
            
            # Create trainer
            trainer = SFTTrainer(
                model=model,
                tokenizer=tokenizer,
                train_dataset=dataset,
                output_dir=config.training.checkpoint_dir
            )
            
            # Train
            history = trainer.train(
                num_epochs=int(num_epochs),
                batch_size=int(batch_size),
                learning_rate=float(learning_rate),
                warmup_steps=int(warmup_steps),
                progress_callback=progress_callback
            )
            
            log_message("SFT обучение завершено!")
            log_message(f"Модель сохранена в {config.training.checkpoint_dir}")
            
        except Exception as e:
            log_message(f"Ошибка обучения: {str(e)}")
            log_message(traceback.format_exc())
        finally:
            training_state["is_training"] = False
            training_state["status"] = "Готов к обучению"
    
    # Start training in background thread
    thread = threading.Thread(target=train_thread)
    thread.start()
    
    return "Обучение запущено! Следите за прогрессом в логах.", "\n".join(training_state["logs"]), get_model_info()


def train_dpo_handler(
    data_path: str,
    num_epochs: int,
    batch_size: int,
    learning_rate: float,
    beta: float
):
    """Start DPO training"""
    global model, tokenizer
    
    if training_state["is_training"]:
        return "Обучение уже запущено!", "\n".join(training_state["logs"]), get_model_info()
    
    if model is None:
        return "Сначала загрузите модель!", "\n".join(training_state["logs"]), get_model_info()
    
    def train_thread():
        try:
            training_state["is_training"] = True
            training_state["status"] = "Обучение DPO..."
            log_message("Начало DPO обучения")
            
            # Create reference model (copy of current model)
            ref_model = SocialSkillsModel(
                vocab_size=model.vocab_size,
                hidden_size=model.hidden_size,
                num_layers=model.num_layers,
                num_heads=model.num_heads,
                max_length=model.max_length
            )
            ref_model.load_state_dict(model.state_dict())
            
            # Create dataset
            dataset = PreferenceDataset(
                data_path=data_path,
                tokenizer=tokenizer,
                max_length=config.model.max_length
            )
            
            if len(dataset) == 0:
                log_message("Ошибка: датасет пуст!")
                training_state["is_training"] = False
                return
            
            log_message(f"Загружено {len(dataset)} примеров предпочтений")
            
            # Create trainer
            trainer = DPOTrainer(
                model=model,
                ref_model=ref_model,
                tokenizer=tokenizer,
                train_dataset=dataset,
                output_dir=config.training.checkpoint_dir,
                beta=float(beta)
            )
            
            # Train
            history = trainer.train(
                num_epochs=int(num_epochs),
                batch_size=int(batch_size),
                learning_rate=float(learning_rate),
                progress_callback=progress_callback
            )
            
            log_message("DPO обучение завершено!")
            
        except Exception as e:
            log_message(f"Ошибка DPO: {str(e)}")
            log_message(traceback.format_exc())
        finally:
            training_state["is_training"] = False
            training_state["status"] = "Готов к обучению"
    
    thread = threading.Thread(target=train_thread)
    thread.start()
    
    return "DPO обучение запущено!", "\n".join(training_state["logs"]), get_model_info()


def save_model_handler():
    """Save current model"""
    global model, tokenizer
    
    if model is None:
        return "Модель не загружена!", "\n".join(training_state["logs"])
    
    try:
        save_path = config.model.model_path
        model.save_pretrained(save_path)
        
        tokenizer_path = config.model.tokenizer_path
        os.makedirs(tokenizer_path, exist_ok=True)
        tokenizer.save_pretrained(tokenizer_path)
        
        log_message(f"Модель сохранена в {save_path}")
        return f"Модель сохранена в {save_path}", "\n".join(training_state["logs"])
    
    except Exception as e:
        log_message(f"Ошибка сохранения: {str(e)}")
        return f"Ошибка: {str(e)}", "\n".join(training_state["logs"])


def test_generation_handler(prompt: str, max_tokens: int, temperature: float):
    """Test model generation"""
    global model, tokenizer
    
    if model is None:
        return "Сначала загрузите модель!"
    
    try:
        model.eval()
        
        # Tokenize
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=config.model.max_length - max_tokens
        )
        
        device = next(model.parameters()).device
        input_ids = inputs["input_ids"].to(device)
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                input_ids=input_ids,
                max_new_tokens=int(max_tokens),
                temperature=float(temperature),
                top_p=0.9,
                top_k=50
            )
        
        # Decode
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return generated
    
    except Exception as e:
        return f"Ошибка генерации: {str(e)}"


def get_training_status():
    """Get current training status"""
    status = f"""
**Статус:** {training_state['status']}
**Обучение:** {'Да' if training_state['is_training'] else 'Нет'}
**Прогресс:** {training_state['progress']}%
**Шаг:** {training_state['current_step']} / {training_state['total_steps']}
**Loss:** {training_state['loss']:.4f}
"""
    return status


def refresh_logs():
    """Refresh logs display"""
    return "\n".join(training_state["logs"][-50:])


def refresh_status():
    """Refresh all status displays"""
    return (
        get_training_status(),
        "\n".join(training_state["logs"][-50:]),
        get_model_info()
    )


# Build Gradio Interface
def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(
        title="Social Skills Model Training",
        theme=gr.themes.Soft()
    ) as interface:
        
        gr.Markdown("""
        # 🎯 Social Skills Model - Training Interface
        
        Интерфейс для обучения модели социальных навыков на PyTorch.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Model Info
                with gr.Group():
                    gr.Markdown("### 📊 Информация о модели")
                    model_info = gr.Markdown(get_model_info())
                    
                    with gr.Row():
                        load_btn = gr.Button("🔄 Загрузить модель", variant="primary")
                        save_btn = gr.Button("💾 Сохранить модель")
                
                # Training Status
                with gr.Group():
                    gr.Markdown("### 📈 Статус обучения")
                    status_display = gr.Markdown(get_training_status())
                    refresh_btn = gr.Button("🔄 Обновить")
            
            with gr.Column(scale=3):
                # Logs
                with gr.Group():
                    gr.Markdown("### 📋 Логи")
                    logs_display = gr.Textbox(
                        value="",
                        lines=15,
                        max_lines=20,
                        label="",
                        interactive=False
                    )
        
        with gr.Tabs():
            # SFT Training Tab
            with gr.Tab("🎓 SFT Обучение"):
                gr.Markdown("""
                **Supervised Fine-Tuning** - обучение на примерах диалогов.
                Формат данных: JSONL с полями `instruction`, `input`, `output`.
                """)
                
                with gr.Row():
                    sft_data_path = gr.Textbox(
                        label="Путь к данным",
                        value="./data/train/sft_data.jsonl",
                        placeholder="Путь к JSONL файлу"
                    )
                
                with gr.Row():
                    sft_epochs = gr.Slider(1, 10, value=3, step=1, label="Эпохи")
                    sft_batch = gr.Slider(1, 32, value=4, step=1, label="Batch Size")
                    sft_lr = gr.Number(value=2e-5, label="Learning Rate")
                    sft_warmup = gr.Slider(0, 1000, value=100, step=10, label="Warmup Steps")
                
                with gr.Row():
                    create_data_btn = gr.Button("📝 Создать примеры данных")
                    train_sft_btn = gr.Button("🚀 Начать SFT обучение", variant="primary")
                
                sft_result = gr.Textbox(label="Результат", lines=2)
            
            # DPO Training Tab
            with gr.Tab("⚖️ DPO Обучение"):
                gr.Markdown("""
                **Direct Preference Optimization** - обучение на предпочтениях.
                Формат данных: JSONL с полями `prompt`, `chosen`, `rejected`.
                """)
                
                with gr.Row():
                    dpo_data_path = gr.Textbox(
                        label="Путь к данным",
                        value="./data/train/preference_data.jsonl",
                        placeholder="Путь к JSONL файлу"
                    )
                
                with gr.Row():
                    dpo_epochs = gr.Slider(1, 5, value=1, step=1, label="Эпохи")
                    dpo_batch = gr.Slider(1, 16, value=2, step=1, label="Batch Size")
                    dpo_lr = gr.Number(value=1e-5, label="Learning Rate")
                    dpo_beta = gr.Slider(0.01, 0.5, value=0.1, step=0.01, label="Beta")
                
                train_dpo_btn = gr.Button("🚀 Начать DPO обучение", variant="primary")
                dpo_result = gr.Textbox(label="Результат", lines=2)
            
            # Test Tab
            with gr.Tab("🧪 Тестирование"):
                gr.Markdown("### Проверка генерации модели")
                
                test_prompt = gr.Textbox(
                    label="Промпт",
                    value="Как подготовиться к сложному разговору с начальником?",
                    lines=3
                )
                
                with gr.Row():
                    test_max_tokens = gr.Slider(50, 500, value=200, label="Max Tokens")
                    test_temp = gr.Slider(0.1, 1.5, value=0.7, step=0.1, label="Temperature")
                
                test_btn = gr.Button("🔮 Сгенерировать", variant="primary")
                test_output = gr.Textbox(label="Результат", lines=10)
            
            # Config Tab
            with gr.Tab("⚙️ Конфигурация"):
                gr.Markdown("### Настройки модели и обучения")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**Модель**")
                        cfg_hidden = gr.Number(value=config.model.hidden_size, label="Hidden Size")
                        cfg_layers = gr.Number(value=config.model.num_layers, label="Num Layers")
                        cfg_heads = gr.Number(value=config.model.num_heads, label="Num Heads")
                        cfg_vocab = gr.Number(value=config.model.vocab_size, label="Vocab Size")
                    
                    with gr.Column():
                        gr.Markdown("**Генерация**")
                        cfg_temp = gr.Slider(0.1, 2.0, value=config.model.temperature, label="Temperature")
                        cfg_top_p = gr.Slider(0.1, 1.0, value=config.model.top_p, label="Top P")
                        cfg_top_k = gr.Slider(1, 100, value=config.model.top_k, label="Top K")
                
                gr.Markdown("""
                **Пути:**
                - Модель: `{}`
                - Чекпоинты: `{}`
                - Данные: `{}`
                """.format(
                    config.model.model_path,
                    config.training.checkpoint_dir,
                    config.data_dir
                ))
        
        # Event handlers
        load_btn.click(
            load_model_handler,
            outputs=[model_info, logs_display]
        )
        
        save_btn.click(
            save_model_handler,
            outputs=[sft_result, logs_display]
        )
        
        refresh_btn.click(
            refresh_status,
            outputs=[status_display, logs_display, model_info]
        )
        
        create_data_btn.click(
            create_sample_data_handler,
            outputs=[logs_display]
        )
        
        train_sft_btn.click(
            train_sft_handler,
            inputs=[sft_data_path, sft_epochs, sft_batch, sft_lr, sft_warmup],
            outputs=[sft_result, logs_display, model_info]
        )
        
        train_dpo_btn.click(
            train_dpo_handler,
            inputs=[dpo_data_path, dpo_epochs, dpo_batch, dpo_lr, dpo_beta],
            outputs=[dpo_result, logs_display, model_info]
        )
        
        test_btn.click(
            test_generation_handler,
            inputs=[test_prompt, test_max_tokens, test_temp],
            outputs=[test_output]
        )
        
        # Auto-refresh logs every 2 seconds during training
        interface.load(
            refresh_logs,
            outputs=[logs_display],
            every=2
        )
    
    return interface


# Main entry point
if __name__ == "__main__":
    print("🚀 Starting Social Skills Model Training Interface...")
    print(f"   Device: {config.training.device}")
    print(f"   GPU Available: {torch.cuda.is_available()}")
    
    interface = create_interface()
    interface.launch(
        server_name=config.gradio_host,
        server_port=config.gradio_port,
        share=False,
        inbrowser=True
    )
