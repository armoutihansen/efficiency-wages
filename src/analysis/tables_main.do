version 19
set more off

capture mkdir results
capture mkdir results/diagnostics
capture mkdir results/diagnostics/tables
capture mkdir results/diagnostics/logs
log using results/diagnostics/logs/stata_main_tables.log, replace text

tempname results
postfile `results' str12 table_id str8 model str48 term double coefficient std_error fit_stat observations using results/diagnostics/tables/main_tables_results.dta, replace

import delimited data/derived/agent_wage_long.csv, clear varnames(1)
keep if treatment == "P" | treatment == "S"
generate treatmentS = treatment == "S"
generate wage_below_5 = .
replace wage_below_5 = 0 if wage > 3
replace wage_below_5 = 1 if wage < 5
xtset n

quietly xtreg acceptance c.wage_below_5, re cluster(n)
post `results' ("Table 2") ("1") ("Wage<5") (_b[wage_below_5]) (_se[wage_below_5]) (e(r2_o)) (e(N))
post `results' ("Table 2") ("1") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_o)) (e(N))

quietly xtreg acceptance c.wage_below_5##c.treatmentS, re cluster(n)
post `results' ("Table 2") ("2") ("Wage<5") (_b[wage_below_5]) (_se[wage_below_5]) (e(r2_o)) (e(N))
post `results' ("Table 2") ("2") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 2") ("2") ("Wage<5*Prosocial treatment") (_b[c.wage_below_5#c.treatmentS]) (_se[c.wage_below_5#c.treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 2") ("2") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_o)) (e(N))

quietly xtreg acceptance c.wage_below_5##c.treatmentS i.gender i.study age, re cluster(n)
post `results' ("Table 2") ("3") ("Wage<5") (_b[wage_below_5]) (_se[wage_below_5]) (e(r2_o)) (e(N))
post `results' ("Table 2") ("3") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 2") ("3") ("Wage<5*Prosocial treatment") (_b[c.wage_below_5#c.treatmentS]) (_se[c.wage_below_5#c.treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 2") ("3") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_o)) (e(N))

quietly xtlogit acceptance c.wage_below_5, re vce(cluster n)
post `results' ("Table 2") ("4") ("Wage<5") (_b[wage_below_5]) (_se[wage_below_5]) (.) (e(N))
post `results' ("Table 2") ("4") ("Constant") (_b[_cons]) (_se[_cons]) (.) (e(N))

quietly xtlogit acceptance c.wage_below_5##c.treatmentS, re vce(cluster n)
post `results' ("Table 2") ("5") ("Wage<5") (_b[wage_below_5]) (_se[wage_below_5]) (.) (e(N))
post `results' ("Table 2") ("5") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (.) (e(N))
post `results' ("Table 2") ("5") ("Wage<5*Prosocial treatment") (_b[c.wage_below_5#c.treatmentS]) (_se[c.wage_below_5#c.treatmentS]) (.) (e(N))
post `results' ("Table 2") ("5") ("Constant") (_b[_cons]) (_se[_cons]) (.) (e(N))

quietly xtlogit acceptance c.wage_below_5##c.treatmentS i.gender i.study age, re vce(cluster n)
post `results' ("Table 2") ("6") ("Wage<5") (_b[wage_below_5]) (_se[wage_below_5]) (.) (e(N))
post `results' ("Table 2") ("6") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (.) (e(N))
post `results' ("Table 2") ("6") ("Wage<5*Prosocial treatment") (_b[c.wage_below_5#c.treatmentS]) (_se[c.wage_below_5#c.treatmentS]) (.) (e(N))
post `results' ("Table 2") ("6") ("Constant") (_b[_cons]) (_se[_cons]) (.) (e(N))

quietly xtreg effort c.wage, re cluster(n)
post `results' ("Table 3") ("1") ("Wage") (_b[wage]) (_se[wage]) (e(r2_o)) (e(N))
post `results' ("Table 3") ("1") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_o)) (e(N))

quietly xtreg effort c.wage##c.treatmentS, re cluster(n)
post `results' ("Table 3") ("2") ("Wage") (_b[wage]) (_se[wage]) (e(r2_o)) (e(N))
post `results' ("Table 3") ("2") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 3") ("2") ("Wage*Prosocial treatment") (_b[c.wage#c.treatmentS]) (_se[c.wage#c.treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 3") ("2") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_o)) (e(N))

quietly xtreg effort c.wage##c.treatmentS i.gender i.study age, re cluster(n)
post `results' ("Table 3") ("3") ("Wage") (_b[wage]) (_se[wage]) (e(r2_o)) (e(N))
post `results' ("Table 3") ("3") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 3") ("3") ("Wage*Prosocial treatment") (_b[c.wage#c.treatmentS]) (_se[c.wage#c.treatmentS]) (e(r2_o)) (e(N))
post `results' ("Table 3") ("3") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_o)) (e(N))

quietly tobit effort c.wage, ul(10) ll(0) vce(cluster n)
post `results' ("Table 3") ("4") ("Wage") (_b[wage]) (_se[wage]) (e(r2_p)) (e(N))
post `results' ("Table 3") ("4") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_p)) (e(N))

quietly tobit effort c.wage##c.treatmentS, ul(10) ll(0) vce(cluster n)
post `results' ("Table 3") ("5") ("Wage") (_b[wage]) (_se[wage]) (e(r2_p)) (e(N))
post `results' ("Table 3") ("5") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2_p)) (e(N))
post `results' ("Table 3") ("5") ("Wage*Prosocial treatment") (_b[c.wage#c.treatmentS]) (_se[c.wage#c.treatmentS]) (e(r2_p)) (e(N))
post `results' ("Table 3") ("5") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_p)) (e(N))

quietly tobit effort c.wage##c.treatmentS i.gender i.study age, ul(10) ll(0) vce(cluster n)
post `results' ("Table 3") ("6") ("Wage") (_b[wage]) (_se[wage]) (e(r2_p)) (e(N))
post `results' ("Table 3") ("6") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2_p)) (e(N))
post `results' ("Table 3") ("6") ("Wage*Prosocial treatment") (_b[c.wage#c.treatmentS]) (_se[c.wage#c.treatmentS]) (e(r2_p)) (e(N))
post `results' ("Table 3") ("6") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2_p)) (e(N))

import delimited data/derived/principals.csv, clear varnames(1)
keep if treatment == "P" | treatment == "S"
generate offered_wage = pa_offer_principal
generate treatmentS = treatment == "S"
generate tSchar = treatmentS * dictatorcharity

quietly regress offered_wage treatmentS, robust
post `results' ("Table 4") ("1") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2)) (e(N))
post `results' ("Table 4") ("1") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2)) (e(N))

quietly regress offered_wage treatmentS dictatorcharity, robust
post `results' ("Table 4") ("2") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2)) (e(N))
post `results' ("Table 4") ("2") ("Charitable motivation") (_b[dictatorcharity]) (_se[dictatorcharity]) (e(r2)) (e(N))
post `results' ("Table 4") ("2") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2)) (e(N))

quietly regress offered_wage treatmentS dictatorcharity tSchar, robust
post `results' ("Table 4") ("3") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2)) (e(N))
post `results' ("Table 4") ("3") ("Charitable motivation") (_b[dictatorcharity]) (_se[dictatorcharity]) (e(r2)) (e(N))
post `results' ("Table 4") ("3") ("Prosocial treatment*Charitable motivation") (_b[tSchar]) (_se[tSchar]) (e(r2)) (e(N))
post `results' ("Table 4") ("3") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2)) (e(N))

quietly regress offered_wage treatmentS dictatorcharity tSchar i.gender i.study age, robust
post `results' ("Table 4") ("4") ("Prosocial treatment") (_b[treatmentS]) (_se[treatmentS]) (e(r2)) (e(N))
post `results' ("Table 4") ("4") ("Charitable motivation") (_b[dictatorcharity]) (_se[dictatorcharity]) (e(r2)) (e(N))
post `results' ("Table 4") ("4") ("Prosocial treatment*Charitable motivation") (_b[tSchar]) (_se[tSchar]) (e(r2)) (e(N))
post `results' ("Table 4") ("4") ("Constant") (_b[_cons]) (_se[_cons]) (e(r2)) (e(N))

postclose `results'

use results/diagnostics/tables/main_tables_results.dta, clear
export delimited using results/diagnostics/tables/main_tables_results.csv, replace

log close
