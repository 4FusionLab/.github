<p align="center"><img src="https://raw.githubusercontent.com/4FusionLab/.github/main/assets/banner.svg" alt="4FusionLab" width="100%"></p>

<h1 align="center">4FusionLab</h1>
<p align="center"><strong>Меньше рутины. Больше проектирования.</strong><br>Независимые инструменты для Autodesk Fusion (Fusion 360), которые упрощают CAD-моделирование, выделение геометрии, управление параметрами и повседневные операции.</p>

<p align="center"><a href="README.md">English</a> · <a href="#доступные-аддоны">Аддоны</a> · <a href="#в-разработке">В разработке</a> · <a href="#каталог-цветов-филаментов">Каталог филаментов</a> · <a href="#для-разработчиков">Разработчикам</a></p>

---

## Доступные аддоны

Скачивайте опубликованные версии из репозиториев соответствующих проектов.

| Проект | Назначение | Статус | Действие |
| --- | --- | --- | --- |
| **[Paramood](https://github.com/4FusionLab/Paramood)** — хранитель меры | Управление пользовательскими и модельными параметрами, формулы с IntelliSense и переключение сохранённых вариантов модели в одной панели. | Stable | [![Paramood latest release](https://img.shields.io/github/v/release/4FusionLab/Paramood?label=release)](https://github.com/4FusionLab/Paramood/releases/latest) |
| **[Perfora](https://github.com/4FusionLab/Perfora)** — богиня отверстий | Параметрическая перфорация, вентиляционные решётки, органические узоры и диаграммы Вороного. | Stable | [![Perfora latest release](https://img.shields.io/github/v/release/4FusionLab/Perfora?label=release)](https://github.com/4FusionLab/Perfora/releases/latest) |
| **[Selectra](https://github.com/4FusionLab/Selectra)** — богиня выбора | Выделение похожих граней и рёбер, поиск замкнутых контуров без лишних кликов. | Stable | [![Selectra latest release](https://img.shields.io/github/v/release/4FusionLab/Selectra?label=release)](https://github.com/4FusionLab/Selectra/releases/latest) |
| **[Ejix](https://github.com/4FusionLab/Ejix)** — дух извлечения | Извлечение объёмов по профилям или плоским граням в отдельные тела и компоненты. | Stable | [![Ejix latest release](https://img.shields.io/github/v/release/4FusionLab/Ejix?label=release)](https://github.com/4FusionLab/Ejix/releases/latest) |
| **[RuEn](https://github.com/4FusionLab/RuEn)** — герой перевода | Работа назначенных горячих клавиш Fusion при русской раскладке на macOS и Windows. | Stable | [![RuEn latest release](https://img.shields.io/github/v/release/4FusionLab/RuEn?label=release)](https://github.com/4FusionLab/RuEn/releases/latest) |

### Создано с Perfora

<p align="center">
<img src="https://raw.githubusercontent.com/4FusionLab/Perfora/main/docs/assets/examples/honeycomb-panel.jpg" alt="Вентиляционная решётка, созданная с Perfora" width="48%">
<img src="https://raw.githubusercontent.com/4FusionLab/Perfora/main/docs/assets/examples/voronoi-panel.jpg" alt="Панель с узором Вороного, созданная с Perfora" width="48%">
</p>

<p align="center"><sub>Больше примеров и инструкция по установке — в <a href="https://github.com/4FusionLab/Perfora">Perfora</a>.</sub></p>

## Размеры в модели

### [Mesora](https://github.com/4FusionLab/Mesora) — информационные размеры в модели

[![Mesora latest release](https://img.shields.io/github/v/release/4FusionLab/Mesora?label=release)](https://github.com/4FusionLab/Mesora/releases/latest)

Информационные 3D-размеры для поддерживаемых расстояний, углов, длин, радиусов, диаметров, площадей и периметров. Определения измерений, ссылки на геометрию, смещения и настройки видимости сохраняются вместе с моделью и восстанавливаются при открытии документа или запуске Mesora. Значения пересчитываются после изменений модели; измерения не создают управляющих ограничений.

**При сохранении исчезает отображаемая графика, а не сохранённые определения измерений.** Откройте Mesora или выполните **Refresh Dimensions**, чтобы снова показать размеры. Без запущенного Mesora модель остаётся доступной для редактирования, а размеры Mesora не отображаются.

Нативная приёмка на macOS охватывает типы измерений, выбор геометрии, видимость, Undo/Redo, изменения модели, сохранение и повторное открытие, переход в Drawing и перезапуск. **Нативное тестирование в Windows Fusion пока не выполнено.** Готовый производственный чертёж и все возможные сценарии сбоев и восстановления облачного сохранения остаются за пределами подтверждённой проверки. Подробности и результаты проверки — в [Mesora](https://github.com/4FusionLab/Mesora).

## В разработке

### [Threader](https://github.com/4FusionLab/Threader) — создание резьбы (заготовка проекта)

Новый репозиторий будущего аддона для построения резьбы в Fusion. Сейчас он содержит неинициализированный общий шаблон аддона, **а не готовый генератор резьбы**.

**Статус: начальная заготовка.** Рабочего аддона и релиза для скачивания пока нет.

### [Planara](https://github.com/4FusionLab/Planara) — богиня плоских миров

Экспериментальный аддон для развёртки выбранных поверхностей твёрдых тел Fusion в плоские выкройки для прототипирования и изготовления.

**Статус: ранняя разработка.** Релиза для скачивания пока нет.

### [Filamentra](https://github.com/4FusionLab/Filamentra) — богиня филаментов

Планируемый аддон для поиска реальных цветов филаментов для 3D-печати по производителям, сериям и оттенкам с установкой визуальных материалов в текущий проект Fusion.

**Статус: планирование / подготовка к разработке.** В репозитории есть артефакты релизов, однако его документация пока не подтверждает работоспособную реализацию для Fusion. Возможности выше остаются планами.

## Каталог цветов филаментов

**[Filamentra DataSource](https://github.com/4FusionLab/Filamentra-DataSource)** — отдельный каталог данных для будущего аддона Filamentra. В нём собираются производители, линейки филаментов, цвета, типы поверхности и ссылки на источники.

**[Открыть интерактивную демоверсию каталога](https://4fusionlab.github.io/Filamentra-DataSource/)** · **[Посмотреть данные](https://github.com/4FusionLab/Filamentra-DataSource)**

Веб-демонстрация показывает данные каталога; документация Filamentra пока не подтверждает работоспособную реализацию аддона Fusion. Оттенки и визуальные эффекты приблизительные и не заменяют инженерные характеристики материалов.

## Для разработчиков

**[Шаблон Fusion Add-in](https://github.com/4FusionLab/.fusion-addin-template)** — основа для новых аддонов Autodesk Fusion: манифест, стартовая команда, офлайн-тесты, CI для нескольких платформ, воспроизводимая сборка релизных архивов, документация на двух языках и правила для агентов в `AGENTS.md`. Перед использованием шаблон необходимо инициализировать.

**[Общая платформа 4FusionLab](https://github.com/4FusionLab/.github)** содержит переиспользуемые процессы сборки и выпуска и [правила оформления README](https://github.com/4FusionLab/.github/blob/main/README_GUIDELINES.ru.md). Это инфраструктурные репозитории, а не аддоны для установки.

## Почему 4FusionLab?

Мы создаём практичные инструменты для инженеров и любителей 3D-моделирования, чтобы больше времени уходило на проектирование, а не на повторяющиеся действия. У каждого аддона — собственный персонаж в авторской мифологии **4FusionLab**, документация, информация о совместимости и место для обратной связи.

Есть идея, вопрос или ошибка? Найдите нужный проект в [списке репозиториев](https://github.com/orgs/4FusionLab/repositories) и откройте Issue.

---

<sub>4FusionLab создаёт независимые проекты, не связанные с Autodesk и не одобренные ею. Лицензии, поддерживаемые платформы и ограничения описаны в репозиториях соответствующих инструментов.</sub>
