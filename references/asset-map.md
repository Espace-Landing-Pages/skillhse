# Карта ассетов

## Компактный рабочий слой

- `assets/tokens/hse.tokens.json` — machine-readable палитра и font families.
- `assets/tokens/hse-tokens.css` — CSS custom properties.
- `assets/tokens/hse-fonts.css` — `@font-face` для HSE Sans и HSE Slab.
- `assets/fonts/hse-sans/` — 6 OTF-файлов.
- `assets/fonts/hse-slab/` — 3 OTF-файла.

## Проверочные примеры

- `assets/examples/hse-training-program-test/` — квадратный digital-постер программы обучения, его HTML-исходник и отдельный синтетический фотослой. Пример проверяет загрузку HSE Sans, официальный SVG-логотип и digital-палитру без изменения исходных бренд-ассетов.

## Полный распакованный набор

- `assets/official/logos/core/` — полные, сокращенные, однострочные и sign-версии для светлого/темного фона.
- `assets/official/logos/campuses/` — Санкт-Петербург, Нижний Новгород, Пермь и Вышка Онлайн.
- `assets/official/logos/divisions/` — двух-/трехстрочные descriptors и варианты с департаментами.
- `assets/official/logos/international/` — полные и сокращенные international-версии.
- `assets/official/graphic-elements/` — аббревиатура, девиз и маскот.
- `assets/official/fonts/` — распакованные официальные font archives.
- `assets/official/templates/presentation/` — PowerPoint и Keynote на русском/английском.
- `assets/official/templates/latex/` — HSE Beamer.
- `assets/official/guidelines/` — полный PDF 2026.

Служебные `__MACOSX`, `.DS_Store` и AppleDouble-файлы удалены. Вложенные ZIP распакованы рекурсивно.

## Выбор формата

| Носитель | Предпочтительный формат | Цветовая модель |
|---|---|---|
| Web/app | SVG | RGB/HEX |
| Social/digital raster | PNG | RGB |
| PowerPoint/Keynote | Встроенный шаблон + SVG/PNG | RGB |
| Профессиональная печать | AI/EPS/PDF | CMYK или Pantone |
| Office print | PDF/PNG высокого разрешения | CMYK/RGB по требованиям подрядчика |

Не использовать JPG для логотипа, если доступен SVG/PDF. Не конвертировать RGB-файл в CMYK «на глаз»; брать готовый официальный вариант.

## Исходные загрузки

`assets/original-downloads/` содержит архивы с официальной страницы под ID или исходным filename. Использовать каталог только для provenance, повторной распаковки и checksum. Для повседневной работы использовать нормализованный `assets/official/`.

Запустить `python3 scripts/unpack_brand_assets.py`, чтобы повторно собрать normalized tree. Скрипт отклоняет path traversal и пропускает macOS metadata.

## Передача команде

Не включать `assets/original-downloads/` и `assets/official/` в обычный Git без Git LFS: полный набор содержит сотни AI/EPS/PDF и занимает более 1 ГБ вместе с архивами. Хранить skill instructions, tokens, scripts и compact fonts в Git; хранить полный asset bundle в закрытом Git LFS, private release или корпоративном файловом хранилище с контролем доступа.
