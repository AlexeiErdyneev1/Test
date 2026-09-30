# Dark Citadel — Production Roadmap

## Definition of done

Каждый новый asset проходит четыре gate'а:

1. **Source lock** — в манифесте зафиксированы версия Terraria, путь, ширина/высота, сетка и количество кадров.
2. **Art review** — соответствие `STYLE_GUIDE.md`, читаемый силуэт на игровом масштабе и отсутствие случайных цветов вне палитры.
3. **Automated validation** — `python3 tools/validate_pack.py --vanilla <Images>` без ошибок.
4. **In-game scene test** — скриншот в реальной сцене: одиночный объект, стык 3×3, анимация или HUD на светлом и тёмном фоне.

> В репозитории не хранятся оригинальные ванильные `.xnb`/PNG. Для source lock художник экспортирует PNG из легальной локальной копии Terraria целевой версии и передаёт в валидатор только путь к ним.

## Этап 1 — Style lock — **готово в 0.1.0**

- [x] Единая палитра и технические правила.
- [x] Темный HUD для наборов Fancy Classic и Horizontal Bars.
- [x] 5 предметов: `Item_1`, `Item_4`, `Item_6`, `Item_7`, `Item_10`.
- [x] 3 terrain-sheet: `Tiles_0`, `Tiles_1`, `Tiles_6`.
- [x] 1 анимированный моб: `NPC_1` с сохранением 2×32×26 кадров.
- [x] Манифест, RGBA/grid-проверка, установочный ZIP.

**Review prompt:** подтвердить, что направление «obsidian + cold cyan + aged gold» — это желаемая интерпретация приложенного референса, прежде чем масштабировать стиль на тысячи файлов.

## Этап 2 — Blocks, Walls & Biomes

### Очерёдность

1. Базовая земля: dirt/stone/grass/mud/clay/sand/snow/ash и их стены.
2. Руды и драгоценные камни: copper → iron → silver → gold → demonite/crimtane → hardmode.
3. Дерево, кирпич и платформы; затем их стены.
4. Растительность, деревья и biome-специфичные стволы/кроны.
5. Parallax background по биомам.

### Gate для тайлов

- один и тот же base-edge во всех frame variants;
- 3×3 тест из однородного материала, затем смесь с соседним материалом;
- тест top/side/corner merge, hammered block и actuated block;
- wall проверяется на бесшовном поле минимум 12×8.

## Этап 3 — Items & Armor

1. Базовые инструменты и оружие по progression tier.
2. Расходники, материалы, аксессуары, боеприпасы.
3. Иконки брони, затем body/head/legs sheets каждого сета.

Для брони тестируются idle, ходьба, прыжок, использование предмета, mount и full-bright свет. Canvas и frame order всегда берутся из установленного источника, а не «на глаз».

## Этап 4 — Town NPC & Enemies

1. Town NPC: Guide, Merchant, Nurse, Arms Dealer, Demolitionist, Clothier, Stylist.
2. Slime-линейка, Demon Eye, zombie/skeleton, bee, Eater of Souls, demon, Crimson enemies.
3. Затем оставшиеся hostile NPC по biome/progression.

Для каждого sheet: frame overlay с источником, loop GIF/видео и hitbox review. Силуэт может стать страшнее, но не выходит за ожидаемые границы кадра и не маскирует телеграфы атаки.

## Этап 5 — Bosses & Complete UI

1. Eye of Cthulhu (обе фазы), Skeletron, Queen Bee, Deerclops, Skeletron Prime, Eater of Worlds.
2. Hotbar/inventory slot sheets, crafting, dialogue, settings, toggles/buttons, карты и прочие UI surfaces.
3. Boss bars, event bars, death/achievement/character-creation flows.

Boss validation: каждое состояние/segment на тёмном и светлом biome-фоне; body parts не получают сдвиг относительно ванильных colliders.

## Этап 6 — Regression, release & support

- clean profile с включённым только Dark Citadel;
- multiplayer client check;
- разные масштабы UI, языки и colorblind/readability review;
- полный artifact manifest и SHA-256;
- changelog с перечислением заменённых игровых path;
- повторная source-dimension validation при каждом обновлении Terraria.

## Release convention

- `0.x`: vertical slices до охвата базовых категорий.
- `1.0`: каждая категория ТЗ имеет согласованный production-ready набор.
- PATCH: только исправления, не меняющие canvas/frame grid.
- MINOR: новые группы textures; они сопровождаются обновлёнными манифестом, валидатором и сценами regression test.
