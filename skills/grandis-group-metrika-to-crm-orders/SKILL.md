---
name: grandis-group-metrika-to-crm-orders
description: Reconcile Yandex Metrika ecommerce purchases with CRM deals or orders by extracting purchase IDs, timestamps, sums, and visit links from the Visitors report, then locating matching records in Bitrix24 or another CRM and assembling a verification table. Use when checking paid-traffic sales, validating monthly advertising reports, comparing Metrika purchase events against CRM data, or building a two-sheet "Metrika vs CRM" order audit.
---

# Grandis Group: Metrika -> CRM Orders

## Overview

Use this skill to move from raw Metrika purchase events to verified CRM orders without binding the workflow to one specific Metrika account, one counter, or one project. The core unit is always the order or purchase ID, not the visitor, phone, or lead.

## Core Principle

Treat Metrika as the source of the fact of purchase, and CRM as the source of the operational order record.

Use Metrika to answer:
- Which purchase IDs were attributed to the selected traffic segment.
- When each purchase event happened.
- What amount Metrika recorded.
- Which visit card contains the event.

Use CRM to answer:
- Whether the order really exists as a deal or order.
- When the CRM record was created.
- What amount and products are in the order.
- What payment information is visible in the order card.

Never rely on names or emails as the primary join key when a purchase ID exists. Search by order ID first.

## When To Use This Workflow

Apply this workflow when the user asks for any of the following:
- Reconcile Metrika purchases with Bitrix24 deals.
- Check whether Metrika sales from ads are present in CRM.
- Build a monthly sales audit for a paid-traffic report.
- Pull order IDs, sums, and timestamps from Metrika visitors.
- Verify paid, partial, or missing CRM orders for a period.
- Fill a Google Sheet with one tab from Metrika and one tab from CRM.

## Inputs To Confirm Before Starting

Confirm or infer these parameters before extraction:
- Date range.
- Traffic segment.
  Examples: ad traffic only, specific source/medium, retargeting only.
- Purchase signal in Metrika.
  Usually this is an ecommerce purchase event inside the Visitors report.
- Target CRM.
  The default pattern below is Bitrix24, but the same logic works for another CRM if it supports order-ID search.
- Output format.
  Example: Google Sheet with two tabs, or one audit table plus notes.

If the user already opened Metrika and CRM in the in-app browser, reuse those tabs instead of opening duplicates.

## Output Structure

Use two datasets.

### Sheet 1: Yandex Metrika

Record at minimum:
- Purchase ID / order ID.
- Purchase date and time from Metrika.
- Purchase sum from Metrika.
- Link to the visit card in Metrika.
- Comment.

Use one row per purchase ID. If one visitor made multiple purchases, create multiple rows.

### Sheet 2: CRM

Record at minimum:
- Order ID.
- Deal or order creation date and time.
- Sum and currency.
- Product list.
- Link to the CRM card.
- Status.
  Example: `найдено`, `не найдено`, `частично найдено`.
- Comment.

## Workflow

### Step 1. Open The Correct Metrika Report

Start from the Visitors report, not from a generic ecommerce summary, because the Visitors report lets you open the visit card and inspect the exact purchase event.

Use this sequence:
1. Set the required period.
2. Apply the required traffic filter.
3. Keep only sessions or visitors relevant to the audit.
4. Work row by row through the filtered visitors list.

If the project uses paid traffic only, also confirm that the filter really limits data to ad traffic before extraction starts.

### Step 2. Open The Visit Card And Extract The Purchase Event

For each relevant visitor:
1. Open the visit card.
2. Open the event timeline.
3. Expand the full event list if the interface hides part of it behind something like `Еще события`.
4. Find the ecommerce purchase event.

Look for one of these markers:
- `ID покупки`
- `Покупка ... на сумму ...`
- order page URLs containing an order parameter
  Example: `/order/?ORDER_ID=26986`

Extract:
- Purchase ID.
- Purchase timestamp.
- Purchase sum.
- Direct link to the visitor or visit card.

If the same visit contains multiple purchase IDs, write each one separately.

If the event list shows several old purchases and one purchase inside the target period, record only the purchase that matches the audit period unless the user explicitly wants all historical purchases from that visitor.

### Step 3. Build The Metrika Order List Before Touching CRM

Finish the first-pass Metrika list before deep CRM checking. This keeps the second stage deterministic.

During this pass:
- Deduplicate by purchase ID.
- Keep comments for unusual cases.
  Examples:
  - multiple purchases in one visitor card;
  - event visible only through order URL;
  - historical purchases mixed with current-period activity.

If the same order ID appears multiple times in Metrika, keep one main row and note the duplicate in the comment.

## Bitrix24 Search Rules

### Step 4. Search CRM By Order ID

In Bitrix24, search by order ID in the deals section.

Important:
- Do not trust a filtered deal list.
- Remove active presets like `Сделки в работе` if they hide part of the funnel.
- If list search behaves inconsistently, use the broader CRM search or a clean unfiltered deals view.

The practical rule is simple:
- If the visible deal search returns nothing but you suspect the order exists, repeat the search in a less filtered surface.
- Prefer the search surface that clearly returns the deal card itself, not only related leads.

When scanning result rows, capture:
- Link to the deal.
- Visible sum.
- Visible creation date.
- Visible order ID in the row.

If search returns only a lead and no deal, do not mark the order as found in CRM. Mark it as `не найдено` and explain that only a lead was found.

### Step 5. Open The Deal Card And Wait For Full Content

Bitrix24 deal cards often render in stages. The first 1-2 seconds may show only the shell, tabs, or buttons.

Use this sequence:
1. Open the deal card.
2. Wait for the card body to finish loading.
3. If the card is inside a side panel or iframe, read the loaded content inside that panel.
4. If only the shell is visible, wait longer and check again.

Do not conclude `not found` or `empty card` too early. Some cards need an additional few seconds before the data block appears.

### Step 6. Extract CRM Fields

Read these fields from the deal card:
- `Номер заказа`
- `Дата создания`
- `Сумма и валюта`
- `Товары`
- payment block
  Examples: `Оплата №...`, `ОПЛАЧЕНО`, `НЕ ОПЛАЧЕНО`, `Итого к оплате`, `Оставшаяся к оплате сумма`

Build the product list exactly as written in the card.

If the product section is truncated behind a control like `Показать ещё`, expand it and re-read the list.

If the interface still keeps part of the list hidden, keep the visible products and explicitly note in the comment that the card contains collapsed positions.

## Payment Interpretation Rules

Do not rely on only one payment signal.

Read payment status in this order:
1. Explicit payment rows inside the payment block.
  Example: `Оплата №26716/1 ... ОПЛАЧЕНО`
2. Remaining payable amount.
3. Custom field or label such as `Статус оплаты`.

Interpretation:
- If an explicit payment row is marked paid and the remaining amount is zero, treat the order as paid even if another field is blank.
- If one payment exists but the remaining amount is still positive, mark it as partial.
- If the payment block contains only placeholder text or no payment entries, note that explicitly instead of inventing a status.
- If the card shows `не заполнено`, preserve that wording in the comment unless stronger payment evidence overrides it.

## Reconciliation Rules

After both sheets are built, compare Metrika and CRM row by row by order ID.

Use these statuses:
- `найдено` when the order exists in CRM.
- `не найдено` when the order does not exist as a CRM order or deal.
- `частично найдено` when only a lead exists or payment data are incomplete.

Note these cases explicitly:
- Metrika has the purchase ID, but CRM has only a lead.
- Metrika and CRM sums differ.
- CRM creation date exists, but Metrika event time is different.
- Several events in Metrika point to the same order ID.
- Several CRM records seem tied to one purchase ID.

## Bitrix24-Specific Notes

When the CRM is Bitrix24:
- Search in deals by order ID first.
- If the current deals view is filtered, remove the preset or switch to a broader search.
- Expect the deal card to open in a side panel.
- Expect partial rendering in the first seconds.

Useful fields commonly visible in Bitrix24:
- `Товары`
- `Дата создания`
- `Сумма и валюта`
- `Оплата и доставка`
- `Итого к оплате по сделке`
- `Оставшаяся к оплате сумма`

## Adaptation To Another CRM

If the project is not in Bitrix24:
- keep the same Metrika extraction stage;
- search the CRM by order ID;
- open the order or opportunity card;
- read the CRM equivalent of creation date, amount, products, payment entries, and remaining amount;
- write the output in the same two-sheet format.

The reusable part of the method is not Bitrix24 itself. The reusable part is:
- extract purchase IDs from Metrika;
- treat purchase ID as the join key;
- verify the order in CRM;
- preserve mismatches and gaps in comments.

## Checklist Before Finishing

Before returning the result:
- Confirm that each Metrika row has a purchase ID.
- Confirm that each CRM row has either a deal link or a reason why it was not found.
- Confirm that duplicate IDs were merged or explained.
- Confirm that `не найдено` is used only after checking an unfiltered or broader CRM search.
- Confirm that collapsed product lists were expanded or flagged.
- Confirm that comments explain every mismatch, payment ambiguity, or search failure.

## Example User Requests

- `Проверь все покупки из Метрики за июль и найди их в Bitrix24.`
- `Собери аудит заказов из Метрики и CRM по рекламе за месяц.`
- `Найди все order ID из отчета Посетители и сверь их со сделками.`
