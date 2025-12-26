import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  TextField,
  InputAdornment,
  Chip,
  List,
  ListItemButton,
  ListItemText,
  Divider,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  MenuBook as BookIcon,
  Psychology as TechniqueIcon,
  Close as CloseIcon,
  CheckCircle as CheckIcon,
  LightbulbOutlined as TipIcon,
  FormatQuote as QuoteIcon,
} from '@mui/icons-material';

const TOPICS = [
  {
    id: 1,
    name: 'Управление конфликтами',
    description: 'Методы и техники разрешения конфликтных ситуаций',
  },
  {
    id: 2,
    name: 'Публичное выступление',
    description: 'Навыки эффективной презентации и ораторского мастерства',
  },
  {
    id: 3,
    name: 'Деловое общение',
    description: 'Коммуникация в профессиональной среде',
  },
  {
    id: 4,
    name: 'Невербальные средства общения',
    description: 'Язык тела, жесты и мимика в коммуникации',
  },
  {
    id: 5,
    name: 'Активное слушание',
    description: 'Техники эффективного восприятия информации',
  },
];

const TECHNIQUES = {
  1: [
    { 
      id: 101, 
      name: 'Техника "Я-сообщения"', 
      description: 'Выражение своих чувств и потребностей без обвинений', 
      difficulty: 'basic',
      content: {
        intro: 'Я-сообщения — это способ выразить свои чувства, мысли и потребности, не обвиняя и не критикуя собеседника. Вместо "Ты всегда опаздываешь!" вы говорите "Я расстраиваюсь, когда приходится ждать".',
        steps: [
          'Опишите ситуацию объективно, без оценок: "Когда встреча начинается позже..."',
          'Выразите свои чувства: "...я чувствую беспокойство..."',
          'Объясните причину: "...потому что у меня много других дел..."',
          'Скажите о своих потребностях: "...мне важно, чтобы мы начинали вовремя"'
        ],
        examples: [
          { bad: 'Ты никогда меня не слушаешь!', good: 'Я чувствую себя неуслышанным, когда мои идеи не обсуждаются' },
          { bad: 'Ты постоянно перебиваешь!', good: 'Мне сложно закончить мысль, когда разговор прерывается' }
        ],
        tips: [
          'Избегайте слов "всегда" и "никогда"',
          'Говорите о конкретной ситуации, а не о характере человека',
          'Фокусируйтесь на своих чувствах, а не на действиях другого'
        ]
      }
    },
    { 
      id: 102, 
      name: 'Метод "Пяти почему"', 
      description: 'Определение истинной причины конфликта', 
      difficulty: 'intermediate',
      content: {
        intro: 'Метод "Пяти почему" помогает докопаться до истинной причины проблемы или конфликта, задавая последовательно вопрос "Почему?" пять раз. Это позволяет выйти за рамки симптомов и найти корневую причину.',
        steps: [
          'Определите проблему или конфликт',
          'Спросите "Почему это произошло?" и запишите ответ',
          'К полученному ответу снова задайте вопрос "Почему?"',
          'Повторите процесс 5 раз (или пока не найдёте корневую причину)',
          'Разработайте решение для корневой причины'
        ],
        examples: [
          { situation: 'Конфликт: коллега не сдал отчёт вовремя', analysis: '1. Почему? — Не хватило времени. 2. Почему? — Было много других задач. 3. Почему? — Нечёткие приоритеты. 4. Почему? — Нет системы планирования. 5. Почему? — Не обучен тайм-менеджменту.' }
        ],
        tips: [
          'Не останавливайтесь на первом ответе',
          'Избегайте обвинений, ищите системные причины',
          'Иногда достаточно 3-4 вопросов'
        ]
      }
    },
    { 
      id: 103, 
      name: 'Компромисс', 
      description: 'Поиск взаимовыгодного решения', 
      difficulty: 'basic',
      content: {
        intro: 'Компромисс — это стратегия разрешения конфликта, при которой обе стороны частично уступают для достижения приемлемого решения. Это не победа и не поражение, а взаимовыгодное соглашение.',
        steps: [
          'Выслушайте позицию другой стороны полностью',
          'Чётко сформулируйте свою позицию и интересы',
          'Найдите общие цели и ценности',
          'Определите, в чём можете уступить без ущерба для главного',
          'Предложите варианты, учитывающие интересы обеих сторон'
        ],
        examples: [
          { situation: 'Спор о графике работы', solution: 'Вместо "только удалёнка" или "только офис" — гибридный формат 3 дня в офисе, 2 дома' }
        ],
        tips: [
          'Компромисс работает, когда обе стороны готовы уступить',
          'Фокусируйтесь на интересах, а не на позициях',
          'Ищите креативные решения, выходящие за рамки "или-или"'
        ]
      }
    },
    { 
      id: 104, 
      name: 'Медиация', 
      description: 'Привлечение третьей стороны для разрешения спора', 
      difficulty: 'advanced',
      content: {
        intro: 'Медиация — это процесс разрешения конфликта с участием нейтрального посредника (медиатора), который помогает сторонам найти взаимоприемлемое решение. Медиатор не принимает решений, а фасилитирует диалог.',
        steps: [
          'Выберите нейтрального медиатора, которому доверяют обе стороны',
          'Установите правила: уважение, конфиденциальность, готовность слушать',
          'Каждая сторона излагает свою позицию без перебивания',
          'Медиатор помогает выявить интересы и потребности',
          'Совместно генерируются варианты решения',
          'Стороны выбирают и фиксируют соглашение'
        ],
        examples: [
          { situation: 'Конфликт между отделами', role: 'HR-менеджер выступает медиатором, помогая найти решение по распределению бюджета' }
        ],
        tips: [
          'Медиатор должен быть беспристрастным',
          'Все стороны должны добровольно участвовать',
          'Соглашение должно быть записано и подписано'
        ]
      }
    },
  ],
  2: [
    { 
      id: 201, 
      name: 'Правило трёх', 
      description: 'Структурирование речи в три части', 
      difficulty: 'basic',
      content: {
        intro: 'Правило трёх — риторический приём, основанный на том, что информация, представленная тройками, легче воспринимается и запоминается. Три пункта создают ощущение полноты и завершённости.',
        steps: [
          'Определите главную идею выступления',
          'Разбейте её на три ключевых аспекта или аргумента',
          'Для каждого аспекта подготовьте примеры и доказательства',
          'Структурируйте: вступление → три основных пункта → заключение'
        ],
        examples: [
          { context: 'Презентация продукта', structure: '1. Проблема клиента, 2. Наше решение, 3. Результаты и выгоды' },
          { context: 'Убеждающая речь', structure: '1. Почему это важно, 2. Что нужно сделать, 3. Какой будет результат' }
        ],
        tips: [
          'Не перегружайте — три пункта, не больше',
          'Используйте параллельную структуру фраз',
          'Знаменитые примеры: "Пришёл, увидел, победил"'
        ]
      }
    },
    { 
      id: 202, 
      name: 'Storytelling', 
      description: 'Использование историй для убеждения', 
      difficulty: 'intermediate',
      content: {
        intro: 'Storytelling — искусство рассказывания историй для передачи идей, ценностей и эмоций. Истории запоминаются в 22 раза лучше, чем факты, и создают эмоциональную связь с аудиторией.',
        steps: [
          'Определите ключевое сообщение истории',
          'Создайте героя, с которым аудитория может себя отождествить',
          'Опишите проблему или вызов, с которым столкнулся герой',
          'Покажите путь решения и трансформацию',
          'Завершите выводом, связанным с вашим посылом'
        ],
        examples: [
          { structure: 'Герой → Проблема → Путь → Трансформация → Мораль', example: '"Год назад наш клиент терял 30% заявок... Мы внедрили систему... Теперь конверсия выросла на 50%"' }
        ],
        tips: [
          'Используйте конкретные детали и имена',
          'Добавляйте эмоции и конфликт',
          'Практикуйте — история должна звучать естественно'
        ]
      }
    },
    { 
      id: 203, 
      name: 'Работа с визуальными материалами', 
      description: 'Эффективное использование презентаций', 
      difficulty: 'basic',
      content: {
        intro: 'Визуальные материалы усиливают воздействие выступления, но только если используются правильно. Плохая презентация может убить даже отличную речь.',
        steps: [
          'Один слайд — одна идея',
          'Минимум текста: не более 6 слов в строке, 6 строк на слайде',
          'Используйте качественные изображения и графики',
          'Контрастные цвета и читаемые шрифты (минимум 24pt)',
          'Слайды дополняют речь, а не дублируют её'
        ],
        examples: [
          { bad: 'Слайд с 10 пунктами мелким шрифтом', good: 'Одна цифра крупно + график' }
        ],
        tips: [
          'Не читайте со слайдов — аудитория сделает это быстрее',
          'Используйте пульт и двигайтесь по сцене',
          'Подготовьте презентацию и без слайдов на случай технических проблем'
        ]
      }
    },
    { 
      id: 204, 
      name: 'Управление голосом', 
      description: 'Техники модуляции и интонации', 
      difficulty: 'intermediate',
      content: {
        intro: 'Голос — главный инструмент оратора. Монотонная речь усыпляет, а правильная модуляция удерживает внимание и передаёт эмоции.',
        steps: [
          'Варьируйте громкость: тише для важного, громче для призыва',
          'Меняйте темп: замедляйтесь на ключевых моментах',
          'Используйте паузы для акцента и осмысления',
          'Следите за дыханием — говорите на выдохе',
          'Артикулируйте чётко, особенно окончания слов'
        ],
        examples: [
          { technique: 'Пауза', usage: 'Перед важной мыслью сделайте паузу 2-3 секунды — аудитория замрёт в ожидании' },
          { technique: 'Шёпот', usage: 'Понизьте голос почти до шёпота — все начнут вслушиваться' }
        ],
        tips: [
          'Записывайте себя и анализируйте',
          'Разминайте голос перед выступлением',
          'Пейте воду комнатной температуры'
        ]
      }
    },
  ],
  3: [
    { 
      id: 301, 
      name: 'Деловая переписка', 
      description: 'Правила составления эффективных писем', 
      difficulty: 'basic',
      content: {
        intro: 'Деловое письмо — это ваша визитная карточка в письменной коммуникации. Чёткое, структурированное письмо экономит время и создаёт профессиональное впечатление.',
        steps: [
          'Тема письма: конкретная и информативная (не "Вопрос", а "Согласование бюджета на Q2")',
          'Приветствие: "Добрый день, Иван" или "Уважаемый Иван Петрович"',
          'Первый абзац: суть обращения в 1-2 предложениях',
          'Основная часть: детали, структурированные списком',
          'Призыв к действию: что вы ждёте от получателя и когда',
          'Подпись: имя, должность, контакты'
        ],
        examples: [
          { subject: 'Плохо: "Встреча"', good: 'Хорошо: "Приглашение на встречу по проекту X, 15 января в 14:00"' }
        ],
        tips: [
          'Одно письмо — один вопрос',
          'Отвечайте в течение 24 часов',
          'Перечитайте перед отправкой'
        ]
      }
    },
    { 
      id: 302, 
      name: 'Сетевое взаимодействие', 
      description: 'Построение профессиональных связей', 
      difficulty: 'intermediate',
      content: {
        intro: 'Нетворкинг — это искусство создания и поддержания профессиональных связей. 85% вакансий закрываются через знакомства, а не через открытые объявления.',
        steps: [
          'Определите цели нетворкинга: карьера, бизнес, знания',
          'Выберите релевантные мероприятия и сообщества',
          'Подготовьте elevator pitch — 30-секундную самопрезентацию',
          'Задавайте вопросы и проявляйте искренний интерес к людям',
          'Обменивайтесь контактами и делайте follow-up в течение 48 часов',
          'Поддерживайте связь: поздравления, полезные материалы'
        ],
        examples: [
          { pitch: '"Привет, я Анна, занимаюсь UX-дизайном в финтехе. Сейчас исследую, как упростить инвестирование для новичков. А вы чем занимаетесь?"' }
        ],
        tips: [
          'Давайте больше, чем берёте',
          'Качество важнее количества контактов',
          'LinkedIn — ваш цифровой нетворкинг'
        ]
      }
    },
    { 
      id: 303, 
      name: 'Этикет переговоров', 
      description: 'Протокол и культура делового общения', 
      difficulty: 'basic',
      content: {
        intro: 'Деловой этикет — это негласные правила, которые создают атмосферу уважения и профессионализма. Нарушение этикета может стоить сделки.',
        steps: [
          'Пунктуальность: приходите за 5 минут до начала',
          'Рукопожатие: уверенное, 2-3 секунды, с зрительным контактом',
          'Визитки: подавайте и принимайте двумя руками, изучите перед тем как убрать',
          'Рассадка: ждите указания хозяина или садитесь напротив партнёра',
          'Телефон: беззвучный режим, на столе экраном вниз',
          'Small talk: начните с нейтральных тем перед делом'
        ],
        examples: [
          { situation: 'Международные переговоры', tip: 'Изучите культурные особенности: в Японии визитки — священны, в США — сразу к делу' }
        ],
        tips: [
          'Dress code: лучше быть немного overdressed',
          'Имена: уточните произношение и запомните',
          'Благодарите за встречу в течение дня'
        ]
      }
    },
    { 
      id: 304, 
      name: 'Фасилитация встреч', 
      description: 'Эффективное ведение совещаний', 
      difficulty: 'advanced',
      content: {
        intro: 'Фасилитация — это навык ведения групповых обсуждений так, чтобы достичь цели встречи, вовлечь всех участников и уложиться во время. Хороший фасилитатор превращает хаос в результат.',
        steps: [
          'До встречи: определите цель, повестку, участников, подготовьте материалы',
          'Начало: озвучьте цель, правила, тайминг',
          'Процесс: следите за временем, вовлекайте молчунов, останавливайте отклонения',
          'Фиксация: записывайте решения и ответственных на доске/экране',
          'Завершение: подведите итоги, назначьте следующие шаги',
          'После: разошлите протокол в течение 24 часов'
        ],
        examples: [
          { technique: 'Parking lot', description: 'Важные, но не относящиеся к теме вопросы записываются отдельно для обсуждения позже' }
        ],
        tips: [
          'Встреча без повестки = потеря времени',
          'Идеальная длительность: 25 или 50 минут',
          'Не более 7 участников для эффективного обсуждения'
        ]
      }
    },
  ],
  4: [
    { 
      id: 401, 
      name: 'Чтение языка тела', 
      description: 'Интерпретация невербальных сигналов', 
      difficulty: 'intermediate',
      content: {
        intro: 'До 93% коммуникации — невербальная. Умение читать язык тела помогает понять истинные эмоции и намерения собеседника, даже когда слова говорят обратное.',
        steps: [
          'Наблюдайте за базовой линией поведения человека',
          'Смотрите на кластеры сигналов, а не отдельные жесты',
          'Учитывайте контекст ситуации',
          'Обращайте внимание на изменения в поведении',
          'Сверяйте невербалику со словами'
        ],
        examples: [
          { signal: 'Скрещённые руки', meaning: 'Не всегда закрытость — может быть холодно или удобно. Смотрите на другие сигналы' },
          { signal: 'Отведённый взгляд', meaning: 'При воспоминании люди смотрят вверх-влево, при конструировании — вверх-вправо' }
        ],
        tips: [
          'Ноги — самая честная часть тела (направлены к интересу)',
          'Микровыражения длятся 1/25 секунды — тренируйте наблюдательность',
          'Не делайте выводов по одному жесту'
        ]
      }
    },
    { 
      id: 402, 
      name: 'Зеркалирование', 
      description: 'Копирование жестов для установления раппорта', 
      difficulty: 'basic',
      content: {
        intro: 'Зеркалирование — это тонкое копирование позы, жестов, темпа речи собеседника для создания подсознательного ощущения близости и доверия. Мы естественно зеркалим тех, кто нам нравится.',
        steps: [
          'Начните с наблюдения за собеседником',
          'Через 10-15 секунд мягко скопируйте позу',
          'Отзеркальте темп и громкость речи',
          'Используйте похожие слова и выражения',
          'Постепенно ведите — меняйте позу и смотрите, следует ли собеседник'
        ],
        examples: [
          { situation: 'Собеседник откинулся на стуле', action: 'Через несколько секунд тоже откиньтесь немного назад' }
        ],
        tips: [
          'Зеркальте тонко, не копируйте буквально',
          'Не зеркальте негативные жесты',
          'Практикуйте в безопасных ситуациях'
        ]
      }
    },
    { 
      id: 403, 
      name: 'Контроль дистанции', 
      description: 'Управление личным пространством', 
      difficulty: 'basic',
      content: {
        intro: 'Проксемика — наука о пространственных отношениях. Правильная дистанция создаёт комфорт, неправильная — напряжение и недоверие.',
        steps: [
          'Интимная зона (0-45 см): только для близких людей',
          'Личная зона (45-120 см): друзья, знакомые',
          'Социальная зона (120-360 см): деловое общение',
          'Публичная зона (более 360 см): выступления'
        ],
        examples: [
          { culture: 'Россия/Европа', distance: 'Комфортная деловая дистанция ~100 см' },
          { culture: 'Латинская Америка', distance: 'Ближе — ~60-80 см' },
          { culture: 'Япония', distance: 'Дальше — ~120-150 см' }
        ],
        tips: [
          'Наблюдайте за реакцией — если человек отступает, дайте пространство',
          'За столом переговоров угловое расположение лучше, чем напротив',
          'В лифте все смотрят на двери — это нормально'
        ]
      }
    },
    { 
      id: 404, 
      name: 'Мимика и эмоции', 
      description: 'Распознавание эмоций по лицу', 
      difficulty: 'intermediate',
      content: {
        intro: 'Пол Экман выделил 7 базовых эмоций, которые одинаково выражаются людьми всех культур: радость, грусть, гнев, страх, удивление, отвращение, презрение.',
        steps: [
          'Радость: уголки губ вверх + морщинки у глаз (улыбка Дюшена)',
          'Грусть: опущенные уголки губ, приподнятые брови изнутри',
          'Гнев: сведённые брови, сжатые губы, расширенные ноздри',
          'Страх: приподнятые брови, широко открытые глаза',
          'Удивление: поднятые брови, открытый рот (кратковременно)',
          'Отвращение: сморщенный нос, приподнятая верхняя губа',
          'Презрение: асимметричная улыбка (один уголок рта вверх)'
        ],
        examples: [
          { emotion: 'Фальшивая улыбка', signs: 'Губы улыбаются, а глаза — нет. Нет "гусиных лапок"' }
        ],
        tips: [
          'Микровыражения проявляются за доли секунды — тренируйте внимание',
          'Смотрите на верхнюю часть лица — её сложнее контролировать',
          'Контекст важен: улыбка на похоронах — не радость'
        ]
      }
    },
  ],
  5: [
    { 
      id: 501, 
      name: 'Парафразирование', 
      description: 'Переформулирование слов собеседника', 
      difficulty: 'basic',
      content: {
        intro: 'Парафразирование — это пересказ своими словами того, что сказал собеседник. Это показывает, что вы слушаете, и помогает избежать недопонимания.',
        steps: [
          'Внимательно выслушайте собеседника до конца',
          'Выделите ключевую мысль',
          'Перескажите её своими словами',
          'Начните с фраз: "Если я правильно понял...", "То есть вы имеете в виду...", "Другими словами..."',
          'Дождитесь подтверждения или уточнения'
        ],
        examples: [
          { original: 'Я устал от этого проекта, всё идёт не так, сроки горят', paraphrase: 'Если я правильно понял, проект вызывает у тебя стресс из-за проблем с дедлайнами?' }
        ],
        tips: [
          'Не повторяйте слово в слово — перефразируйте',
          'Фокусируйтесь на содержании, не на эмоциях (для этого есть отражение чувств)',
          'Используйте, когда информация важна или сложна'
        ]
      }
    },
    { 
      id: 502, 
      name: 'Открытые вопросы', 
      description: 'Задавание вопросов для углубления диалога', 
      difficulty: 'basic',
      content: {
        intro: 'Открытые вопросы начинаются с "Что", "Как", "Почему", "Расскажи" и требуют развёрнутого ответа. Они приглашают к диалогу и показывают интерес.',
        steps: [
          'Замените закрытые вопросы на открытые',
          'Используйте: Что? Как? Почему? Каким образом? Расскажите...',
          'Избегайте вопросов с очевидным ответом',
          'Дайте время на обдумывание — не торопите',
          'Слушайте ответ, задавайте уточняющие вопросы'
        ],
        examples: [
          { closed: 'Тебе понравилась презентация?', open: 'Что ты думаешь о презентации?' },
          { closed: 'Ты согласен?', open: 'Как ты относишься к этому предложению?' }
        ],
        tips: [
          '"Почему" может звучать как обвинение — используйте "Что привело к..."',
          'Не задавайте несколько вопросов сразу',
          'Молчание после вопроса — это нормально'
        ]
      }
    },
    { 
      id: 503, 
      name: 'Эмпатическое присутствие', 
      description: 'Полное внимание к собеседнику', 
      difficulty: 'intermediate',
      content: {
        intro: 'Эмпатическое присутствие — это состояние полного внимания к собеседнику, когда вы откладываете свои мысли, оценки и советы и просто НАХОДИТЕСЬ рядом с человеком.',
        steps: [
          'Уберите отвлекающие факторы (телефон, компьютер)',
          'Повернитесь к собеседнику, установите зрительный контакт',
          'Отпустите свои мысли и желание ответить',
          'Сосредоточьтесь на словах, эмоциях, невербалике',
          'Позвольте паузам быть — не заполняйте их',
          'Отражайте эмоции: "Похоже, тебя это расстраивает"'
        ],
        examples: [
          { situation: 'Коллега делится проблемой', wrong: 'Да ладно, не переживай, у меня было хуже', right: 'Звучит непросто. Расскажи подробнее, что произошло' }
        ],
        tips: [
          'Не давайте советов, пока не попросят',
          'Ваша задача — понять, а не решить',
          'Присутствие иногда важнее слов'
        ]
      }
    },
    { 
      id: 504, 
      name: 'Резюмирование', 
      description: 'Подведение итогов разговора', 
      difficulty: 'basic',
      content: {
        intro: 'Резюмирование — это краткое подведение итогов сказанного, которое помогает структурировать разговор, проверить понимание и зафиксировать договорённости.',
        steps: [
          'Выделите ключевые пункты разговора',
          'Структурируйте их логически',
          'Начните с фраз: "Итак, мы обсудили...", "Подводя итог...", "Давай зафиксируем..."',
          'Перечислите основные моменты и решения',
          'Уточните следующие шаги и ответственных',
          'Спросите: "Я ничего не упустил?"'
        ],
        examples: [
          { context: 'Конец совещания', summary: '"Итак, мы решили: 1) запустить пилот в марте, 2) Иван готовит план, 3) встречаемся через неделю. Всё верно?"' }
        ],
        tips: [
          'Резюмируйте в конце встречи и при смене темы',
          'Используйте резюме для завершения затянувшегося разговора',
          'Отправьте письменное резюме после важных встреч'
        ]
      }
    },
  ],
};

function LibraryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedTechnique, setSelectedTechnique] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [topics] = useState(TOPICS);
  const [techniques, setTechniques] = useState([]);

  useEffect(() => {
    if (selectedTopic) {
      setTechniques(TECHNIQUES[selectedTopic.id] || []);
    } else {
      const allTechniques = Object.values(TECHNIQUES).flat();
      setTechniques(allTechniques);
    }
  }, [selectedTopic]);

  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
  };

  const handleTechniqueClick = (technique) => {
    setSelectedTechnique(technique);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const filteredTechniques = techniques.filter((technique) =>
    technique.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    technique.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Библиотека знаний
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Изучайте техники эффективной коммуникации
        </Typography>
      </Box>

      <TextField
        fullWidth
        placeholder="Поиск техник и материалов..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon color="action" />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 4 }}
      />

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BookIcon /> Темы
          </Typography>
          <Card>
            <List disablePadding>
              <ListItemButton
                selected={!selectedTopic}
                onClick={() => setSelectedTopic(null)}
              >
                <ListItemText primary="Все темы" />
              </ListItemButton>
              <Divider />
              {topics.map((topic) => (
                <ListItemButton
                  key={topic.id}
                  selected={selectedTopic?.id === topic.id}
                  onClick={() => handleTopicSelect(topic)}
                >
                  <ListItemText
                    primary={topic.name}
                    secondary={topic.description}
                  />
                </ListItemButton>
              ))}
            </List>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TechniqueIcon /> 
            {selectedTopic ? `Техники: ${selectedTopic.name}` : 'Все техники'}
          </Typography>
          
          <Grid container spacing={2}>
            {filteredTechniques.map((technique) => (
              <Grid item xs={12} sm={6} key={technique.id}>
                <Card sx={{ height: '100%' }}>
                  <CardActionArea 
                    sx={{ p: 2, height: '100%' }}
                    onClick={() => handleTechniqueClick(technique)}
                  >
                    <CardContent sx={{ p: 0 }}>
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <Chip
                          label={
                            technique.difficulty === 'advanced' ? 'Продвинутый' :
                            technique.difficulty === 'intermediate' ? 'Средний' :
                            'Базовый'
                          }
                          size="small"
                          color={
                            technique.difficulty === 'advanced' ? 'error' :
                            technique.difficulty === 'intermediate' ? 'warning' :
                            'success'
                          }
                        />
                      </Box>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        {technique.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {technique.description}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
            {filteredTechniques.length === 0 && (
              <Grid item xs={12}>
                <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  Техники не найдены
                </Typography>
              </Grid>
            )}
          </Grid>
        </Grid>
      </Grid>

      {/* Диалог с уроком */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, maxHeight: '90vh' }
        }}
      >
        {selectedTechnique && (
          <>
            <DialogTitle sx={{ pr: 6 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Chip
                  label={
                    selectedTechnique.difficulty === 'advanced' ? 'Продвинутый' :
                    selectedTechnique.difficulty === 'intermediate' ? 'Средний' :
                    'Базовый'
                  }
                  size="small"
                  color={
                    selectedTechnique.difficulty === 'advanced' ? 'error' :
                    selectedTechnique.difficulty === 'intermediate' ? 'warning' :
                    'success'
                  }
                />
              </Box>
              <Typography variant="h5" fontWeight={700}>
                {selectedTechnique.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedTechnique.description}
              </Typography>
              <IconButton
                onClick={handleCloseDialog}
                sx={{ position: 'absolute', right: 8, top: 8 }}
              >
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent dividers>
              {selectedTechnique.content && (
                <Box>
                  {/* Введение */}
                  <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.7 }}>
                    {selectedTechnique.content.intro}
                  </Typography>

                  {/* Шаги */}
                  {selectedTechnique.content.steps && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 3 }}>
                        <CheckIcon color="success" /> Как применять
                      </Typography>
                      <Box component="ol" sx={{ pl: 2 }}>
                        {selectedTechnique.content.steps.map((step, index) => (
                          <Box 
                            component="li" 
                            key={index}
                            sx={{ 
                              mb: 1.5, 
                              pl: 1,
                              '&::marker': { fontWeight: 600, color: 'primary.main' }
                            }}
                          >
                            <Typography variant="body1">{step}</Typography>
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Примеры */}
                  {selectedTechnique.content.examples && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 3 }}>
                        <QuoteIcon color="primary" /> Примеры
                      </Typography>
                      {selectedTechnique.content.examples.map((example, index) => (
                        <Card 
                          key={index} 
                          sx={{ 
                            mb: 2, 
                            backgroundColor: 'action.hover',
                            border: '1px solid',
                            borderColor: 'divider'
                          }}
                        >
                          <CardContent>
                            {example.bad && example.good && (
                              <>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                                  <Chip label="✗" size="small" color="error" sx={{ minWidth: 32 }} />
                                  <Typography variant="body2" sx={{ textDecoration: 'line-through', opacity: 0.7 }}>
                                    {example.bad}
                                  </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                                  <Chip label="✓" size="small" color="success" sx={{ minWidth: 32 }} />
                                  <Typography variant="body2" fontWeight={500}>
                                    {example.good}
                                  </Typography>
                                </Box>
                              </>
                            )}
                            {example.situation && example.solution && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>Ситуация:</strong> {example.situation}
                                </Typography>
                                <Typography variant="body2">
                                  <strong>Решение:</strong> {example.solution}
                                </Typography>
                              </>
                            )}
                            {example.situation && example.analysis && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>Ситуация:</strong> {example.situation}
                                </Typography>
                                <Typography variant="body2">
                                  <strong>Анализ:</strong> {example.analysis}
                                </Typography>
                              </>
                            )}
                            {example.situation && example.role && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>Ситуация:</strong> {example.situation}
                                </Typography>
                                <Typography variant="body2">
                                  {example.role}
                                </Typography>
                              </>
                            )}
                            {example.context && example.structure && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>{example.context}:</strong>
                                </Typography>
                                <Typography variant="body2">
                                  {example.structure}
                                </Typography>
                              </>
                            )}
                            {example.structure && example.example && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>Структура:</strong> {example.structure}
                                </Typography>
                                <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                                  {example.example}
                                </Typography>
                              </>
                            )}
                            {example.technique && example.usage && (
                              <>
                                <Typography variant="body2" fontWeight={600} gutterBottom>
                                  {example.technique}
                                </Typography>
                                <Typography variant="body2">
                                  {example.usage}
                                </Typography>
                              </>
                            )}
                            {example.subject && example.good && (
                              <>
                                <Typography variant="body2" sx={{ textDecoration: 'line-through', opacity: 0.7 }} gutterBottom>
                                  {example.subject}
                                </Typography>
                                <Typography variant="body2" fontWeight={500}>
                                  {example.good}
                                </Typography>
                              </>
                            )}
                            {example.pitch && (
                              <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                                {example.pitch}
                              </Typography>
                            )}
                            {example.culture && example.distance && (
                              <>
                                <Typography variant="body2" fontWeight={600}>
                                  {example.culture}
                                </Typography>
                                <Typography variant="body2">
                                  {example.distance}
                                </Typography>
                              </>
                            )}
                            {example.signal && example.meaning && (
                              <>
                                <Typography variant="body2" fontWeight={600}>
                                  {example.signal}
                                </Typography>
                                <Typography variant="body2">
                                  {example.meaning}
                                </Typography>
                              </>
                            )}
                            {example.emotion && example.signs && (
                              <>
                                <Typography variant="body2" fontWeight={600}>
                                  {example.emotion}
                                </Typography>
                                <Typography variant="body2">
                                  {example.signs}
                                </Typography>
                              </>
                            )}
                            {example.original && example.paraphrase && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>Оригинал:</strong> "{example.original}"
                                </Typography>
                                <Typography variant="body2">
                                  <strong>Парафраз:</strong> "{example.paraphrase}"
                                </Typography>
                              </>
                            )}
                            {example.closed && example.open && (
                              <>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                                  <Chip label="Закрытый" size="small" color="default" />
                                  <Typography variant="body2" sx={{ opacity: 0.7 }}>
                                    {example.closed}
                                  </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                                  <Chip label="Открытый" size="small" color="success" />
                                  <Typography variant="body2" fontWeight={500}>
                                    {example.open}
                                  </Typography>
                                </Box>
                              </>
                            )}
                            {example.situation && example.wrong && example.right && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>Ситуация:</strong> {example.situation}
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                                  <Chip label="✗" size="small" color="error" sx={{ minWidth: 32 }} />
                                  <Typography variant="body2" sx={{ opacity: 0.7 }}>
                                    {example.wrong}
                                  </Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                                  <Chip label="✓" size="small" color="success" sx={{ minWidth: 32 }} />
                                  <Typography variant="body2" fontWeight={500}>
                                    {example.right}
                                  </Typography>
                                </Box>
                              </>
                            )}
                            {example.context && example.summary && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>{example.context}:</strong>
                                </Typography>
                                <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                                  "{example.summary}"
                                </Typography>
                              </>
                            )}
                            {example.technique && example.description && (
                              <>
                                <Typography variant="body2" fontWeight={600}>
                                  {example.technique}
                                </Typography>
                                <Typography variant="body2">
                                  {example.description}
                                </Typography>
                              </>
                            )}
                            {example.situation && example.action && !example.wrong && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>Ситуация:</strong> {example.situation}
                                </Typography>
                                <Typography variant="body2">
                                  <strong>Действие:</strong> {example.action}
                                </Typography>
                              </>
                            )}
                            {example.situation && example.tip && (
                              <>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  <strong>{example.situation}:</strong>
                                </Typography>
                                <Typography variant="body2">
                                  {example.tip}
                                </Typography>
                              </>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </Box>
                  )}

                  {/* Советы */}
                  {selectedTechnique.content.tips && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 3 }}>
                        <TipIcon color="warning" /> Советы
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {selectedTechnique.content.tips.map((tip, index) => (
                          <Box 
                            key={index}
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'flex-start', 
                              gap: 1,
                              p: 1.5,
                              borderRadius: 2,
                              backgroundColor: 'warning.main',
                              color: 'warning.contrastText',
                              '& .MuiTypography-root': { color: 'inherit' }
                            }}
                          >
                            <Typography variant="body2" fontWeight={600}>💡</Typography>
                            <Typography variant="body2">{tip}</Typography>
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
              )}
            </DialogContent>
            <DialogActions sx={{ p: 2 }}>
              <Button onClick={handleCloseDialog} variant="contained" size="large">
                Закрыть
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}

export default LibraryPage;
