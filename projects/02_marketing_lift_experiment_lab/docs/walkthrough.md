# How to use the experiment lab

## 1. Start with the decision

Open the dashboard. The initial view is Retargeting campaign, Evaluation, All customers and All devices. It uses 60,285 users. The treatment rate is 8.02%, the control rate is 6.71%, and the lift is +1.32 percentage points.

The four cards show assignment count, conversion lift and its interval, extra conversions per 1,000 treated and net contribution per 1,000 treated. The chart compares conversion rates. The line below it shows the effect interval with a zero reference. The counts table provides the numerators and denominators.

## 2. Change a control

| Control | What it changes |
| --- | --- |
| Experiment | Selects the main campaign, the smaller test or the deliberately broken extract |
| Data split | Evaluation is the final comparison. Development is for choosing a customer group and always shows Development only |
| Customer type | Applies All, New or Returning to the decision metrics, counts and record examples |
| Device | Applies All, Desktop or Mobile to the same measures. Device slices are exploratory |
| Reset | Restores the main campaign, Evaluation, All customers, All devices and the default cost inputs. It clears record search. It does not reset the separate planning inputs |
| Cost / assigned treatment user | Changes the hypothetical CAD treatment cost. Valid range is 0 to 20 |
| Contribution / extra conversion | Changes hypothetical CAD contribution per incremental conversion. Valid range is 0 to 1,000 |
| Export selection CSV | Downloads one row with current filters, raw counts, lift bounds, cost assumptions, net estimate and decision. It includes synthetic and exploratory flags |

At cost CAD 0.60 and contribution CAD 90, break-even lift is 0.67 percentage points. The main result has estimated net contribution of CAD 584 per 1,000 treated. Change cost to CAD 1.60 and the interval falls below zero. Conversion rates stay the same. Clear a cost input or enter a negative value and the dashboard asks you to fix it.

The full-experiment SRM check always remains in force. Selecting Returning or Mobile cannot clear a broken experiment. For that experiment, outcome and financial estimates are withheld in the decision view and summary export. Example records remain available as diagnostics.

## 3. Compare customer groups

Open Customer groups. The table shows New and Returning for the selected experiment, split and device. It deliberately ignores the customer-type filter so both rows stay visible. The text above the table makes that exception clear.

Development chooses the group with the larger lower effect bound, using all devices. In the main campaign that is Returning. The evaluation check for that fixed group uses 24,242 users and shows +2.58 percentage points of lift. Other slices are exploratory. These separate intervals do not establish a difference between groups.

## 4. Trace a record

Open Example records. The initial evaluation view shows 24 fixed examples. These are the first three users from each customer type × device × arm cell. They are not the data used to estimate the main effect.

Search for retargeting_000017, then click the user. The dialog shows assignment time, split, arm, exposure, purchase count and converted flag. It has two purchases inside the window and a later purchase outside the window. Converted still equals 1. Close dismisses the dialog.

Search for an unknown ID to see the empty state. The examples export becomes disabled. Clear the search or widen a filter to restore results. Export shown examples downloads only the rows currently visible under the filters and search.

## 5. Plan a test

Open Plan a test. Baseline conversion rate and Minimum increase are independent of the campaign filters. The default 7% baseline and 1 percentage-point increase give approximately 10,890 users per arm, or 21,780 total.

Changing the minimum increase to 0.5 points requires more users. Inputs must be positive and add to less than 100%. An invalid combination shows a useful message. The calculation assumes equal allocation, a fixed horizon, 80% power and two-sided alpha of 5%. It is not the current result's probability of being correct.

## 6. Check an inconclusive case

Select Small campaign test and Evaluation, with All customers and All devices. Its conversion interval crosses zero. At the default cost, the upper net bound is just below zero. Change the cost to CAD 0.30 to see Inconclusive at this cost. Cost should come from the business, not be selected to get a preferred answer.

## 7. Read the analysis and definitions

How I calculated it explains outcome grain, assignment versus exposure, the split, SRM and financial rules. Read the analysis opens the executed HTML notebook view. The GitHub project has the original notebook, script, SQL, data generator, actual output tables and tests.

## 8. Run and host it

Follow the README commands. Serve dist/ over HTTP. No server-side Python or live ad account is needed to use the saved dashboard. Later it can be placed on GitHub Pages without changing the interaction model. Regenerating the analysis still requires Python. The hosted preview is owner-private, and website integration remains a separate step.
