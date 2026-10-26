# Data challenges

Twelve years of my own booking history sounds like clean data. It was not. Here is what went wrong, with the numbers.

This is the published subset of the full log kept in the private workspace. Entries about the Apple Health side of the project are not here, because none of that data is published and no figure in the Reel rests on it. Instructors' names are left out throughout.

## 1. The first five and a half years have no cancellations

376 of the 957 reservations carry a `created_at` of 2020-07-07, even though those classes ran between 2014-12-04 and 2020-03-05. That is the day my old history was migrated into the studio's current booking system. All 376 are check-ins — no cancellations survived the move.

So two questions can only be answered from mid-2021 on: how often I cancel, and how far ahead I book. Everything before that has a booking timestamp that is really a migration timestamp. It is still in the published file, so anyone computing lead times has to drop it the same way.

## 2. The export identifies instructors by name, and names collide

The instructor column — spelled `instrutor` in the file, which is its own small surprise — holds full names and nothing else. No identifier. That matters because first names repeat: **seven first names in my history each belong to two different people**, and one of those pairs covers 39 classes with one instructor and 31 with the other.

The analysis keyed on the full name to keep them apart. The published file does not: it carries first names only, so those seven pairs are merged there. That is a deliberate trade — the people who taught me did not sign up to be in a public dataset.

## 3. Two-instructor classes don't say who led

106 reservations list two instructors. The names are always in alphabetical order by first name, so the order tells you nothing about who actually led the class. A further 31 reservations name no instructor at all.

The rule I settled on: the lead is whoever taught more of my single-instructor classes. That resolves 105 of the 106, and one pair ties — both instructors had taught me zero solo classes before that day.

It is a rule with a known bias. The instructor I have seen most taught 255 solo classes, so the rule always makes him the lead, including in pairs where he may well have been assisting. The weakest cases are the ones where the nominal "lead" has only two or three solo classes to the other's zero.

## 4. Class names and spot labels changed under us

The class type reads "TREMBLE Group Classes/Megaformer" until 2019-09-21, "TREMBLE Group Classes/Reformer" from 2019-09-28 to 2020-03-05, and "Full Body TREMBLE" from the June 2021 return onward. Machine numbers are plain (1–18) except between 2021 and 2023, when they are written `R-1` to `R-9`.

It was the same product on the same machines throughout, so both changes are relabeling. But the `R-` labels hint at something real: at the main studio, every booking from June 2021 to mid-2023 uses one — 25 in 2021, 121 in 2022, 58 in 2023 — and **none goes above spot 9**, against spots up to 18 before COVID and after. That fits a room running fewer machines for distancing.

It stays a candidate explanation, not a finding. These are my bookings, so the highest spot I personally booked is a floor on the room's size, not a count of it.

## 5. No "rescheduled" status, and no waitlist

The statuses are: check in (777), standard cancel (163), penalty cancel (8), cancelled by the studio (3), pending (3 classes after the export date), and one each of graced cancel, graced no-show and penalty no-show.

There is no "rescheduled". A reschedule looks exactly like a cancellation plus a new booking, so it has to be inferred rather than read. Six classes were booked more than once — one day in August 2021 was booked and cancelled twice, at both 9:30 and 10:30.

## 6. "Books 28 days ahead" turned out to be a wall, not a habit

The single most common lead time in my bookings is 28 days, which looked like a decision until I checked the distribution either side of it. The longest lead time in twelve years is **30.0 days**, two bookings sit at 30, and **nothing exceeds 31**. A distribution that climbs to a peak and then stops dead is a software limit, not a preference.

So "he plans a month ahead" was describing the app's booking window. The interesting part is narrower and better evidenced: of the bookings at 28–29 days, 50 are Sunday-to-Sunday and 71 were made on a day I was already at the studio. It is a ritual attached to the class, not a planning habit.

The count also moves with the rounding. `booked_days_ahead` is the gap between two timestamps, so it is fractional: counting "28 days" three different ways gives 3 bookings, 93, or 99. Any figure like that needs its rounding rule stated.

## 7. The booking window itself moved, so there is no baseline

The 30-day ceiling has not always been there — the app changed in 2020 and began allowing bookings further ahead.

That puts two walls between this data and a twelve-year trend. The first five and a half years have no booking dates at all (#1), and the years that do straddle a platform change. So any "how far ahead" series starts at mid-2021 and can never be set against the pre-2020 era.

It cuts the other way too, usefully. The window widened in 2020, but my median lead time was still 5.5 days in late 2021 and only reached 25 days in early 2023 — about two years behind the change. Whatever moved, it was not the app.

## 8. A cancellation can happen after the class has already started

`hours_cancelled_before` goes negative. Of the eight reservations that drew a late-cancel penalty, **seven have a negative value** — between one and four hours *after* the class began. Only one was cancelled in advance at all.

So the column is a signed offset, not a duration, and any "how far ahead does he cancel" figure has to say whether negatives are dropped, clamped or kept. It changes the answer: this analysis finds a median of 55 hours across 175 cancellations since 2021, and an earlier pass found 59, with the difference coming entirely from which rows were counted.

Those same rows undercut treating the penalty as a commitment device: **28 cancellations fell inside 12 hours of the class, but only 8 drew a penalty.** Either the window is not 12 hours or it is applied by hand.
