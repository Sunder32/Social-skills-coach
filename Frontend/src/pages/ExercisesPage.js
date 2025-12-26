import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Check as CheckIcon,
  Timer as TimerIcon,
  Add as AddIcon,
  Close as CloseIcon,
  NavigateNext as NextIcon,
  Replay as RetryIcon,
} from '@mui/icons-material';

// Упражнения с реальными заданиями и проверкой
const EXERCISES = [
  {
    id: 1,
    title: 'Просьба о помощи',
    description: 'Учимся корректно просить помощь у других людей, не создавая неловкости',
    difficulty: 'easy',
    duration: 5,
    category: 'communication',
    type: 'multi_step',
    steps: [
      {
        type: 'theory',
        title: 'Теория',
        content: `Правильная просьба о помощи состоит из 4 элементов:
        
1. **Конкретика** — чётко опишите, что нужно
2. **Причина** — объясните, почему вам нужна помощь
3. **Уважение времени** — признайте, что человек может быть занят
4. **Благодарность** — поблагодарите заранее

❌ Плохо: "Помоги мне"
✅ Хорошо: "Не мог бы ты помочь мне разобраться с отчётом? Я застрял на формулах, и мне нужен свежий взгляд. Понимаю, что ты занят — если сейчас неудобно, скажи когда сможешь. Буду очень благодарен!"`,
      },
      {
        type: 'quiz',
        title: 'Выберите лучший вариант',
        question: 'Вам нужно попросить коллегу проверить ваш код. Какой вариант лучше?',
        options: [
          'Проверь мой код, срочно нужно.',
          'Можешь глянуть код? Там что-то не работает.',
          'Привет! Не мог бы ты посмотреть мой код, когда будет время? Я уже 2 часа ищу баг и не могу найти. Понимаю, что у тебя свои задачи — если занят, скажи. Заранее спасибо!',
          'У тебя есть время? Мне нужна помощь.'
        ],
        correctAnswer: 2,
        explanation: 'Третий вариант содержит все элементы хорошей просьбы: конкретику (посмотреть код), причину (2 часа ищу баг), уважение времени (если занят), благодарность.'
      },
      {
        type: 'practice',
        title: 'Практика',
        scenario: 'Вы работаете над презентацией и вам нужна помощь коллеги с дизайном слайдов. Напишите просьбу о помощи.',
        criteria: [
          { keyword: ['помочь', 'помощь', 'посмотреть', 'взглянуть', 'мог бы', 'могла бы'], label: 'Вежливая форма просьбы' },
          { keyword: ['презентац', 'слайд', 'дизайн'], label: 'Конкретика — что нужно' },
          { keyword: ['потому что', 'так как', 'нужн', 'важно', 'не получается', 'сложно'], label: 'Причина просьбы' },
          { keyword: ['занят', 'время', 'когда удобно', 'если можешь', 'не срочно'], label: 'Уважение времени' },
          { keyword: ['спасибо', 'благодар', 'признателен'], label: 'Благодарность' }
        ],
        minCriteria: 3
      }
    ]
  },
  {
    id: 2,
    title: 'Разрешение конфликта',
    description: 'Навыки дипломатичного разрешения споров и недопониманий',
    difficulty: 'medium',
    duration: 10,
    category: 'conflict',
    type: 'multi_step',
    steps: [
      {
        type: 'theory',
        title: 'Теория: Я-сообщения',
        content: `**Я-сообщения** — способ выразить недовольство без обвинений.

Формула: **"Когда [ситуация], я чувствую [эмоция], потому что [причина]. Мне важно [потребность]"**

❌ Ты-сообщение: "Ты всегда опаздываешь! Тебе наплевать на других!"
✅ Я-сообщение: "Когда встреча начинается позже, я чувствую беспокойство, потому что у меня плотный график. Мне важно начинать вовремя."

**Почему это работает:**
- Не вызывает защитную реакцию
- Фокус на ваших чувствах, а не на "вине" другого
- Открывает диалог, а не эскалирует конфликт`,
      },
      {
        type: 'quiz',
        title: 'Преобразуйте в Я-сообщение',
        question: 'Коллега громко разговаривает по телефону, мешая вам работать. Какой ответ — правильное Я-сообщение?',
        options: [
          'Ты слишком громко говоришь, это невозможно терпеть!',
          'Можно потише? Люди работают.',
          'Когда рядом громкий разговор, мне сложно сосредоточиться на задаче. Не мог бы ты говорить чуть тише или выйти в переговорку?',
          'Почему ты всегда такой громкий?'
        ],
        correctAnswer: 2,
        explanation: 'Это Я-сообщение: описывает ситуацию без обвинений, выражает влияние на вас и предлагает решение.'
      },
      {
        type: 'practice',
        title: 'Практика',
        scenario: 'Ваш друг третий раз отменяет встречу в последний момент. Вы расстроены. Напишите Я-сообщение.',
        criteria: [
          { keyword: ['когда', 'в ситуации', 'в момент'], label: 'Описание ситуации (Когда...)' },
          { keyword: ['чувствую', 'ощущаю', 'расстраиваюсь', 'обидно', 'неприятно', 'грустно'], label: 'Выражение чувств' },
          { keyword: ['потому что', 'так как', 'ведь', 'поскольку'], label: 'Объяснение причины' },
          { keyword: ['важно', 'хотелось бы', 'нужно', 'прошу', 'давай'], label: 'Выражение потребности' }
        ],
        minCriteria: 3,
        badPatterns: ['ты всегда', 'ты никогда', 'ты постоянно', 'тебе наплевать', 'ты не ценишь']
      }
    ]
  },
  {
    id: 3,
    title: 'Публичное выступление',
    description: 'Подготовка и проведение короткой презентации перед аудиторией',
    difficulty: 'hard',
    duration: 15,
    category: 'public_speaking',
    type: 'multi_step',
    steps: [
      {
        type: 'theory',
        title: 'Структура выступления',
        content: `**Правило трёх** — структурируйте речь в 3 части:

**1. Вступление (10%)** — зацепите внимание
- Интригующий факт или статистика
- Провокационный вопрос
- Короткая история

**2. Основная часть (80%)** — три ключевых пункта
- Один пункт — одна идея
- Примеры и доказательства для каждого
- Логические переходы между пунктами

**3. Заключение (10%)** — призыв к действию
- Резюме ключевых идей
- Чёткий призыв: что делать дальше
- Запоминающаяся финальная фраза`,
      },
      {
        type: 'quiz',
        title: 'Структура презентации',
        question: 'С чего лучше начать презентацию нового продукта?',
        options: [
          'Здравствуйте, меня зовут... и я расскажу о...',
          'Наш продукт имеет следующие характеристики...',
          '78% компаний теряют клиентов из-за медленной поддержки. Что если бы вы могли отвечать за 30 секунд?',
          'Спасибо, что пришли. Давайте начнём.'
        ],
        correctAnswer: 2,
        explanation: 'Статистика + провокационный вопрос сразу захватывают внимание и создают интригу. Скучное "меня зовут" можно сказать позже.'
      },
      {
        type: 'practice',
        title: 'Практика',
        scenario: 'Напишите вступление (2-3 предложения) для презентации вашего проекта команде. Используйте один из приёмов: факт/статистику, вопрос или мини-историю.',
        criteria: [
          { keyword: ['%', 'процент', 'раз', 'млн', 'тысяч', 'исследовани'], label: 'Использование статистики/факта' },
          { keyword: ['?'], label: 'Риторический вопрос' },
          { keyword: ['представьте', 'вообразите', 'история', 'однажды', 'случай', 'когда я'], label: 'Элемент истории' },
          { keyword: ['проблем', 'вызов', 'сложност', 'задач'], label: 'Обозначение проблемы' }
        ],
        minCriteria: 2
      },
      {
        type: 'quiz',
        title: 'Завершение выступления',
        question: 'Как лучше закончить презентацию?',
        options: [
          'Ну вот, собственно, и всё. Есть вопросы?',
          'Итак, мы рассмотрели три способа повысить продуктивность. Начните с первого уже сегодня — и через неделю увидите результат. Действуйте!',
          'Спасибо за внимание.',
          'Я закончил. Можете задавать вопросы.'
        ],
        correctAnswer: 1,
        explanation: 'Хорошее завершение: резюме + конкретный призыв к действию + мотивирующая фраза.'
      }
    ]
  },
  {
    id: 4,
    title: 'Отказ без обиды',
    description: 'Учимся вежливо отказывать, сохраняя хорошие отношения',
    difficulty: 'medium',
    duration: 7,
    category: 'boundaries',
    type: 'multi_step',
    steps: [
      {
        type: 'theory',
        title: 'Техника мягкого отказа',
        content: `**Формула вежливого отказа:**

1. **Благодарность** — "Спасибо, что подумал обо мне..."
2. **Отказ** — чётко, но мягко: "К сожалению, не смогу..."
3. **Причина** (опционально) — краткая, без оправданий
4. **Альтернатива** — предложите другой вариант

**Примеры:**
❌ "Нет, я занят" (грубо)
❌ "Ну ладно, хорошо..." (не честно с собой)
✅ "Спасибо за приглашение! К сожалению, в субботу не смогу — у меня уже есть планы. Но давай встретимся на следующей неделе?"

**Важно:** вы имеете право отказывать без объяснения причин!`,
      },
      {
        type: 'quiz',
        title: 'Выберите лучший отказ',
        question: 'Коллега просит вас поработать в выходные, но у вас планы с семьёй. Как отказать?',
        options: [
          'Нет, не могу.',
          'Ну... ладно, приду... (вздыхая)',
          'Спасибо, что обратился! В эти выходные, к сожалению, не получится — семейные планы. Могу помочь в понедельник с утра или посмотреть, что можно сделать в пятницу вечером. Как тебе?',
          'У меня дела, извини.'
        ],
        correctAnswer: 2,
        explanation: 'Здесь есть благодарность, мягкий отказ с краткой причиной и две альтернативы. Это показывает уважение и готовность помочь иначе.'
      },
      {
        type: 'practice',
        title: 'Практика',
        scenario: 'Друг просит одолжить денег, но вы не хотите. Напишите вежливый отказ.',
        criteria: [
          { keyword: ['спасибо', 'ценю', 'понимаю'], label: 'Благодарность/эмпатия' },
          { keyword: ['не смогу', 'не получится', 'к сожалению', 'не могу'], label: 'Чёткий отказ' },
          { keyword: ['может', 'давай', 'попробуй', 'вариант', 'альтернатив', 'помочь иначе'], label: 'Альтернатива' }
        ],
        minCriteria: 2,
        badPatterns: ['отстань', 'не хочу', 'мне всё равно']
      }
    ]
  },
  {
    id: 5,
    title: 'Активное слушание',
    description: 'Практика техник активного слушания и эмпатии',
    difficulty: 'easy',
    duration: 5,
    category: 'empathy',
    type: 'multi_step',
    steps: [
      {
        type: 'theory',
        title: 'Техники активного слушания',
        content: `**5 техник активного слушания:**

1. **Парафраз** — пересказ своими словами
   "Если я правильно понял, ты говоришь что..."

2. **Отражение чувств** — назовите эмоцию
   "Похоже, тебя это расстраивает..."

3. **Уточняющие вопросы** — копайте глубже
   "Что ты имеешь в виду под...?"

4. **Минимальные поощрения** — покажите, что слушаете
   "Угу", "Понимаю", "Да", кивки

5. **Резюмирование** — подведите итог
   "Итак, главное — это..."

**Чего избегать:**
❌ Перебивать
❌ Давать советы, когда не просят
❌ Говорить "Я тебя понимаю, у меня тоже..."`,
      },
      {
        type: 'quiz',
        title: 'Выберите лучший ответ',
        question: 'Коллега говорит: "Я так устал от этого проекта, ничего не получается, менеджер постоянно меняет требования". Что ответить?',
        options: [
          'Да ладно, не переживай, всё будет нормально!',
          'У меня тоже так было на прошлом проекте...',
          'Звучит очень frustrating — требования меняются, и ты чувствуешь, что твоя работа обесценивается. Что больше всего напрягает?',
          'Тебе надо поговорить с менеджером.'
        ],
        correctAnswer: 2,
        explanation: 'Это отражение чувств + парафраз + уточняющий вопрос. Показывает, что вы слышите и хотите понять глубже.'
      },
      {
        type: 'practice',
        title: 'Практика',
        scenario: 'Друг говорит: "Я провалил собеседование. Готовился неделю, а они сказали, что у меня мало опыта". Напишите ответ с использованием активного слушания.',
        criteria: [
          { keyword: ['понимаю', 'чувству', 'обидно', 'разочарован', 'расстроен', 'тяжело', 'неприятно'], label: 'Отражение чувств' },
          { keyword: ['готовился', 'неделю', 'опыт', 'собеседован'], label: 'Парафраз ситуации' },
          { keyword: ['?'], label: 'Уточняющий вопрос' }
        ],
        minCriteria: 2,
        badPatterns: ['не переживай', 'забей', 'не расстраивайся', 'ерунда', 'найдёшь другую']
      }
    ]
  },
  {
    id: 6,
    title: 'Комплименты и похвала',
    description: 'Учимся искренне хвалить людей',
    difficulty: 'easy',
    duration: 5,
    category: 'communication',
    type: 'multi_step',
    steps: [
      {
        type: 'theory',
        title: 'Искусство комплимента',
        content: `**Хороший комплимент:**

1. **Конкретный** — не "молодец", а что именно хорошо
2. **Искренний** — говорите только то, во что верите
3. **О действиях, не о человеке** — "отличная презентация" vs "ты умный"

**Формула:** "Мне понравилось, как ты [конкретное действие], особенно [деталь]"

**Примеры:**
❌ "Отлично!" (непонятно что)
❌ "Ты такой умный!" (звучит наигранно)
✅ "Мне понравилось, как ты структурировал презентацию — особенно переход от проблемы к решению, очень убедительно."

**Бонус:** комплимент усилиям ценнее комплимента таланту`,
      },
      {
        type: 'quiz',
        title: 'Выберите лучший комплимент',
        question: 'Коллега провёл сложные переговоры и получил хорошие условия. Как похвалить?',
        options: [
          'Молодец!',
          'Ты прирождённый переговорщик!',
          'Круто, что договорились!',
          'Впечатляет, как ты выдержал паузу, когда они давили на цену — это помогло получить скидку. Отлично сработано!'
        ],
        correctAnswer: 3,
        explanation: 'Конкретика (выдержал паузу), связь с результатом (получил скидку), похвала действия.'
      },
      {
        type: 'practice',
        title: 'Практика',
        scenario: 'Ваш друг научился готовить и угостил вас ужином. Еда была вкусной. Напишите конкретный искренний комплимент.',
        criteria: [
          { keyword: ['понравил', 'вкусн', 'отлично', 'здорово', 'круто', 'впечатл'], label: 'Позитивная оценка' },
          { keyword: ['соус', 'мяс', 'овощ', 'специ', 'приготов', 'рецепт', 'подача', 'текстур'], label: 'Конкретная деталь' }
        ],
        minCriteria: 2
      }
    ]
  }
];

function ExercisesPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [stepResult, setStepResult] = useState(null);
  const [exerciseScore, setExerciseScore] = useState(0);
  
  const [addedExercises, setAddedExercises] = useState(() => {
    const saved = localStorage.getItem('addedExercises');
    return saved ? JSON.parse(saved) : [];
  });
  
  const [completedExercises, setCompletedExercises] = useState(() => {
    const saved = localStorage.getItem('completedExercises');
    return saved ? JSON.parse(saved) : {};
  });

  const [exerciseResults, setExerciseResults] = useState(() => {
    const saved = localStorage.getItem('exerciseResults');
    return saved ? JSON.parse(saved) : {};
  });

  useEffect(() => {
    localStorage.setItem('addedExercises', JSON.stringify(addedExercises));
  }, [addedExercises]);

  useEffect(() => {
    localStorage.setItem('completedExercises', JSON.stringify(completedExercises));
  }, [completedExercises]);

  useEffect(() => {
    localStorage.setItem('exerciseResults', JSON.stringify(exerciseResults));
  }, [exerciseResults]);

  const handleAddExercise = (exerciseId) => {
    if (!addedExercises.includes(exerciseId)) {
      setAddedExercises([...addedExercises, exerciseId]);
      setActiveTab(1);
    }
  };

  const isExerciseAdded = (exerciseId) => addedExercises.includes(exerciseId);
  const isExerciseCompleted = (exerciseId) => !!completedExercises[exerciseId];

  const handleStartExercise = (exercise) => {
    setSelectedExercise(exercise);
    setCurrentStep(0);
    setUserAnswer('');
    setSelectedOption(null);
    setStepResult(null);
    setExerciseScore(0);
  };

  const checkPracticeAnswer = (answer, criteria, badPatterns) => {
    const lowerAnswer = answer.toLowerCase();
    let matchedCriteria = [];
    let feedback = [];
    
    // Проверка на плохие паттерны
    if (badPatterns) {
      for (const pattern of badPatterns) {
        if (lowerAnswer.includes(pattern.toLowerCase())) {
          return {
            success: false,
            score: 0,
            feedback: `⚠️ Избегайте фраз типа "${pattern}". Это может вызвать защитную реакцию. Попробуйте переформулировать.`,
            matchedCriteria: []
          };
        }
      }
    }

    // Проверка критериев
    for (const criterion of criteria) {
      const matched = criterion.keyword.some(kw => lowerAnswer.includes(kw.toLowerCase()));
      if (matched) {
        matchedCriteria.push(criterion.label);
        feedback.push(`✅ ${criterion.label}`);
      } else {
        feedback.push(`❌ ${criterion.label}`);
      }
    }

    const score = Math.round((matchedCriteria.length / criteria.length) * 100);
    const minCriteria = criteria.length > 2 ? Math.ceil(criteria.length * 0.6) : 2;
    const success = matchedCriteria.length >= minCriteria;

    return {
      success,
      score,
      feedback: feedback.join('\n'),
      matchedCriteria,
      minRequired: minCriteria
    };
  };

  const handleSubmitStep = () => {
    if (!selectedExercise) return;
    
    const step = selectedExercise.steps[currentStep];
    setIsSubmitting(true);

    setTimeout(() => {
      let result = null;

      if (step.type === 'quiz') {
        const isCorrect = selectedOption === step.correctAnswer;
        result = {
          success: isCorrect,
          score: isCorrect ? 100 : 0,
          feedback: isCorrect 
            ? `✅ Правильно!\n\n${step.explanation}`
            : `❌ Неправильно. Правильный ответ: "${step.options[step.correctAnswer]}"\n\n${step.explanation}`
        };
      } else if (step.type === 'practice') {
        if (userAnswer.trim().length < 20) {
          result = {
            success: false,
            score: 0,
            feedback: '⚠️ Ответ слишком короткий. Напишите более развёрнуто (минимум 20 символов).'
          };
        } else {
          result = checkPracticeAnswer(userAnswer, step.criteria, step.badPatterns);
        }
      }

      if (result) {
        setStepResult(result);
        setExerciseScore(prev => prev + result.score);
      }

      setIsSubmitting(false);
    }, 500);
  };

  const handleNextStep = () => {
    if (currentStep < selectedExercise.steps.length - 1) {
      setCurrentStep(prev => prev + 1);
      setUserAnswer('');
      setSelectedOption(null);
      setStepResult(null);
    } else {
      // Завершение упражнения
      const totalSteps = selectedExercise.steps.filter(s => s.type !== 'theory').length;
      const finalScore = Math.round(exerciseScore / totalSteps);
      
      setCompletedExercises(prev => ({
        ...prev,
        [selectedExercise.id]: {
          completedAt: new Date().toISOString(),
          score: finalScore
        }
      }));
      
      setExerciseResults(prev => ({
        ...prev,
        [selectedExercise.id]: [...(prev[selectedExercise.id] || []), {
          date: new Date().toISOString(),
          score: finalScore
        }]
      }));

      setAddedExercises(prev => prev.filter(id => id !== selectedExercise.id));
    }
  };

  const handleCloseDialog = () => {
    setSelectedExercise(null);
    setCurrentStep(0);
    setUserAnswer('');
    setSelectedOption(null);
    setStepResult(null);
    setExerciseScore(0);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  const getDifficultyLabel = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'Легкий';
      case 'medium': return 'Средний';
      case 'hard': return 'Сложный';
      default: return difficulty;
    }
  };

  const getFilteredExercises = () => {
    if (activeTab === 0) return EXERCISES;
    if (activeTab === 1) return EXERCISES.filter(ex => addedExercises.includes(ex.id) && !completedExercises[ex.id]);
    return EXERCISES.filter(ex => completedExercises[ex.id]);
  };

  const filteredExercises = getFilteredExercises();
  const completedCount = Object.keys(completedExercises).length;
  const progressPercentage = (completedCount / EXERCISES.length) * 100;

  const renderStepContent = () => {
    if (!selectedExercise) return null;
    const step = selectedExercise.steps[currentStep];

    if (step.type === 'theory') {
      return (
        <Box>
          <Typography 
            variant="body1" 
            sx={{ 
              whiteSpace: 'pre-line',
              '& strong': { color: 'primary.main' }
            }}
            dangerouslySetInnerHTML={{ 
              __html: step.content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/❌/g, '<span style="color: #f44336">❌</span>')
                .replace(/✅/g, '<span style="color: #4caf50">✅</span>')
            }}
          />
        </Box>
      );
    }

    if (step.type === 'quiz') {
      return (
        <Box>
          <Typography variant="h6" gutterBottom>
            {step.question}
          </Typography>
          <FormControl component="fieldset" sx={{ width: '100%', mt: 2 }}>
            <RadioGroup
              value={selectedOption}
              onChange={(e) => setSelectedOption(parseInt(e.target.value))}
            >
              {step.options.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={index}
                  control={<Radio />}
                  label={option}
                  disabled={!!stepResult}
                  sx={{
                    mb: 1,
                    p: 1,
                    borderRadius: 2,
                    backgroundColor: stepResult 
                      ? index === step.correctAnswer 
                        ? 'success.main' 
                        : index === selectedOption 
                          ? 'error.main' 
                          : 'transparent'
                      : 'transparent',
                    '& .MuiFormControlLabel-label': {
                      color: stepResult && (index === step.correctAnswer || index === selectedOption) 
                        ? 'white' 
                        : 'text.primary'
                    }
                  }}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </Box>
      );
    }

    if (step.type === 'practice') {
      return (
        <Box>
          <Box sx={{ p: 2, mb: 3, backgroundColor: 'action.hover', borderRadius: 2, border: '1px dashed', borderColor: 'divider' }}>
            <Typography variant="subtitle2" color="primary.main" gutterBottom>
              Сценарий:
            </Typography>
            <Typography variant="body1">
              {step.scenario}
            </Typography>
          </Box>
          
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Напишите ваш ответ..."
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            disabled={!!stepResult}
          />
          
          {!stepResult && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                💡 Подсказка: постарайтесь включить в ответ: {step.criteria.map(c => c.label.toLowerCase()).join(', ')}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }
  };

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Упражнения
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Практикуйтесь в различных коммуникативных сценариях
        </Typography>
      </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Общий прогресс
              </Typography>
              <LinearProgress variant="determinate" value={progressPercentage} sx={{ height: 8, borderRadius: 4 }} />
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700} color="primary.main">{completedCount}</Typography>
              <Typography variant="caption" color="text.secondary">Выполнено</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" fontWeight={700}>{EXERCISES.length}</Typography>
              <Typography variant="caption" color="text.secondary">Всего</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Все" />
        <Tab label={<Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          Мои упражнения
          {addedExercises.filter(id => !completedExercises[id]).length > 0 && (
            <Chip label={addedExercises.filter(id => !completedExercises[id]).length} size="small" color="primary" />
          )}
        </Box>} />
        <Tab label="Выполнены" />
      </Tabs>

      <Grid container spacing={3}>
        {filteredExercises.map((exercise) => {
          const isAdded = isExerciseAdded(exercise.id);
          const isCompleted = isExerciseCompleted(exercise.id);
          const lastScore = completedExercises[exercise.id]?.score;
          
          return (
            <Grid item xs={12} sm={6} md={4} key={exercise.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip label={getDifficultyLabel(exercise.difficulty)} size="small" color={getDifficultyColor(exercise.difficulty)} />
                    {isCompleted && (
                      <Chip icon={<CheckIcon />} label={`${lastScore}%`} size="small" color="success" variant="outlined" />
                    )}
                  </Box>
                  <Typography variant="h6" gutterBottom>{exercise.title}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>{exercise.description}</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                    <TimerIcon fontSize="small" />
                    <Typography variant="caption">~{exercise.duration} мин</Typography>
                  </Box>
                </CardContent>
                
                <CardActions sx={{ p: 2, pt: 0 }}>
                  {activeTab === 0 && !isCompleted && (
                    isAdded ? (
                      <Button fullWidth variant="outlined" color="success" startIcon={<CheckIcon />} disabled>Добавлено</Button>
                    ) : (
                      <Button fullWidth variant="contained" startIcon={<AddIcon />} onClick={() => handleAddExercise(exercise.id)}>Добавить</Button>
                    )
                  )}
                  {activeTab === 1 && (
                    <Button fullWidth variant="contained" startIcon={<StartIcon />} onClick={() => handleStartExercise(exercise)}>Начать</Button>
                  )}
                  {(activeTab === 2 || (activeTab === 0 && isCompleted)) && (
                    <Button fullWidth variant="outlined" startIcon={<RetryIcon />} onClick={() => handleStartExercise(exercise)}>Повторить</Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {filteredExercises.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {activeTab === 1 && 'Нет добавленных упражнений'}
            {activeTab === 2 && 'Нет выполненных упражнений'}
          </Typography>
        </Box>
      )}

      {/* Диалог упражнения */}
      <Dialog open={!!selectedExercise} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        {selectedExercise && (
          <>
            <DialogTitle sx={{ pb: 1 }}>
              <Typography variant="h5" fontWeight={600}>{selectedExercise.title}</Typography>
              <Typography variant="body2" color="text.secondary">{selectedExercise.description}</Typography>
            </DialogTitle>
            
            <DialogContent dividers>
              <Stepper activeStep={currentStep} sx={{ mb: 3 }}>
                {selectedExercise.steps.map((step, index) => (
                  <Step key={index}>
                    <StepLabel>{step.title}</StepLabel>
                  </Step>
                ))}
              </Stepper>

              {renderStepContent()}

              {stepResult && (
                <Alert 
                  severity={stepResult.success ? 'success' : 'error'} 
                  sx={{ mt: 3, whiteSpace: 'pre-line' }}
                >
                  {stepResult.feedback}
                </Alert>
              )}
            </DialogContent>
            
            <DialogActions sx={{ p: 2 }}>
              <Button onClick={handleCloseDialog}>Закрыть</Button>
              
              {selectedExercise.steps[currentStep].type === 'theory' ? (
                <Button variant="contained" onClick={handleNextStep} endIcon={<NextIcon />}>
                  Продолжить
                </Button>
              ) : !stepResult ? (
                <Button 
                  variant="contained" 
                  onClick={handleSubmitStep}
                  disabled={(selectedExercise.steps[currentStep].type === 'quiz' && selectedOption === null) || 
                           (selectedExercise.steps[currentStep].type === 'practice' && !userAnswer.trim()) ||
                           isSubmitting}
                >
                  {isSubmitting ? <CircularProgress size={20} /> : 'Проверить'}
                </Button>
              ) : (
                <Button variant="contained" onClick={handleNextStep} endIcon={<NextIcon />}>
                  {currentStep < selectedExercise.steps.length - 1 ? 'Далее' : 'Завершить'}
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}

export default ExercisesPage;
