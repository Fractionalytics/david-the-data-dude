# Data challenges: voting

What got in the way while checking the numbers, written for curious non-engineers.

## Getting the data

1. **"What percent of people voted?" has three right answers.** In 2024, three measures gave three different turnout figures:
   - 64.3% of *eligible* voters, counting real ballots (UF Election Lab).
   - 65.3% of citizens who *said* they voted (Census survey).
   - 88.7% of *registered* citizens who said they voted.

   The "60% of registered voters" that's often quoted mixes up the first and the third.
2. **People fib about voting, politely.** The Census survey asks people whether they voted. In 2020, 66.8% of citizens said yes, while the official count shows 66.4% of eligible voters turned out. In 2022 the gap was wider: 52.2% said yes, against 46.1% who actually voted. The two don't share a denominator exactly: the survey counts citizens 18+, while the official rate also leaves out people barred from voting, such as some people with felony convictions. Even so, survey turnout runs high, so any "registered voter" rate built from it does too.
3. **A news story and Gallup itself disagreed about a record.** Syndicated coverage of Gallup's 2026 poll said average confidence in institutions was 3 points *below* the prior record low. Gallup's own release says it is 27%, which is one point *above* the record low of 26% set in 2023. Always go back to the pollster.

4. **The same lab, two answers for 2020.** UF Election Lab's national file puts 2020 turnout at 66.38%. Its state-by-state file, whose "United States" row has the head counts, gives 65.99%. The two files are different versions. From 1998 to 2008 they also count different things: total ballots in one, votes for the top race in the other, a gap of up to 1.1 points (in 2000, 55.3% against 54.2%). We use the national file for percentages and the state file only for head counts.

5. **Turnout by age has two measures, and the better one is short.** The Census survey reports turnout by age as a share of *citizens* only from 2002. Before that, it's a share of *everyone* that age, noncitizens included, which runs lower: in 2022, 25.6% of all 18–24-year-olds against 27.6% of citizens that age. The long age trend uses the "everyone" measure and starts in 1972, the first election after the 26th Amendment lowered the voting age to 18.

5b. **Half the young people vanish before 1972.** The Census counts 13.0 million 18–24-year-olds in 1970 and 24.6 million in 1972. They didn't double in two years: before the 26th Amendment, most 18–20-year-olds couldn't vote, so the survey mostly left them out of this group. Population charts by age start in 1972.

6. **Who was in Congress on a given day is surprisingly slippery.** The member database dates early terms from the first session, not the legal start: the term starting December 2, 1901 belongs to a Congress that legally began March 4. A snapshot taken on March 15, 1901 found only 57 members. We switched to December 31 of each Congress's first year, which finds 533 in 2025. Our averages still run about 0.5 years below Congress's own research service (House 57.4 against 57.9 in 2025), probably because of how each counts birthdays.

## Classifying / judgment calls

7. **Rates hid the real story; headcounts found it.** Our first test compared turnout *rates* by age and concluded that older voters' edge stopped growing after 2002 while Congress kept aging. David asked about the size of the 65+ group. Multiplying each age group's population by its turnout showed that 65+ voters went from 23.2% of the 2002 midterm electorate to 30.4% in 2022, because the baby boomers aged in. A rate tells you how likely each person is to vote. A share tells you who's in the room.

8. **"All-time low" is almost true, and that's the trap.** Confidence in Congress is 9% in 2026. The record is 7%, set twice, in 2014 and 2022. The broader measure of trust in the federal government sits at 17%, and its single lowest poll was 10% in 2011. Both are near the floor, but neither is at it.
9. **Two "trust" questions that sound alike aren't alike.**
   - Gallup asks how much *confidence* you have in Congress, and its trend starts in 1973.
   - Pew's compilation asks whether you *trust the government in Washington* to do what's right. It stitches together polls from six pollsters back to 1958.

   They move together, but you can't splice one into the other.
