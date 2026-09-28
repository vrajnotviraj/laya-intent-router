"""Synthetic training workflows: healthcare clinic appointments & pharmacy. Run: python training/synth3/synth_3_a.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import write

A1 = """
@wf synth3_a_01_sunrise_family_clinic
#path greeting
= hi
= hello
= Customer is greeting the clinic or saying hello
- hi || sh
- hello || sh
- hey there || sh,s
- hiii || t,sh
- good morning || p,sh
- good evening doctor || p
- helo || t,sh
- hi how are you || q
- hey || sh
- hello sunrise clinic || sh
- morning! || sh
- yo || s,sh
- hi good afternoon || p
- hellooo || t,sh
- hi there, hope you're well || p
- gm || s,sh
- hey hey || s,sh
- greetings || p,sh
- hello hello || sh
- hi 👋 || sh
- hey! || sh
- hullo || t,sh
- good afternoon || p,sh
- hi team || sh
#path book_appointment
= book an appointment
= i want to see a doctor
= Patient wants to schedule a new visit with a doctor
- i want to book an appointment || sh
- need to see a doctor tomorrow || e
- can i get an appointment with dr patel on friday || q,e
- book me in for a checkup pls || s
- my son has a fever since 2 days, can we come in today || m,e
- apointment for next monday morning || t,e
- i'd like to schedule a visit please || p
- any slots available this week? || q
- need a doctor visit for my back pain || e
- can i make a booking for 3 ppl, me my wife and daughter || e,s
- first time patient, how do i book || q
- want to see a dermatologist || e
- book appt || s,sh
- i need a general physician appointment around 5pm || e
- my mom needs a follow up with dr rao, can you book that || e,i
- i havent been feeling well for a week. can someone see me || m,i
- schedule me for a flu shot on 12 oct || e
- is dr khan free on saturday? i want to book || q,e
- new appointment please || sh,p
- can i book online through here || q
- need a pediatrician slot for my 4 year old || e
- book a consultation for tomorrow 10am, name is sarah jones || e
- wanna see a doc asap || s
- hi, i need to get my blood pressure checked, can i come in thursday || m,e
#path reschedule_appointment
= change my appointment time
= move my booking to another day
= Patient wants to shift an existing appointment to a different date or time
- can i change my appointment to next week || q
- need to move my booking from tuesday to thursday || e
- reschedule appt #45821 pls || e,s
- i cant make it at 3pm, can we do 5 instead || i,e
- push my appointment to friday || sh,e
- something came up at work, can i come another day instead || m,i
- change the time of my visit with dr patel || e
- my appointment is tomorrow but i need a later slot || i
- resceduel my checkup || t
- can you shift my 10:30 to afternoon || e
- is it possible to move my appointment to next month? || q,p
- i booked for the 14th but want the 16th || e,i
- postpone my appointment by a week || e
- need a different date for my follow up, booking id SF-2291 || e
- change my booking time please || p,sh
- can we swap my appointment to the morning || i
- running late, can i take a later slot today instead || i,m
- my daughter has exams monday, move her appointment to wednesday || e,m
- rebook me for another day, same doctor || i
- could you please reschedule my visit, thank you || p
- i need to change my appointment date || sh
- the timing doesnt work anymore, need to shift my appointment || i
- can i move my appointment to the evening || q
- switch my dr rao appointment from 4 to 6 pm || e
#path cancel_appointment
= cancel my appointment
= Patient no longer wants an existing appointment and wants it called off
- cancel my appointment || sh
- please cancel my booking for tomorrow || p,e
- i wont be coming on friday, cancel it || i,e
- cancel appt SF-3310 || e,sh
- i dont need the appointment anymore || i
- my fever is gone, no need for the visit, please cancel || m,i
- cancell my checkup || t
- remove my booking with dr khan || e
- call off my appointment for the 20th || e
- i want to cancel, not reschedule || n
- can i cancel my appointment? || q
- cancel my son's appointment please, he's better now || p,m
- we're travelling, cancel all my bookings || e,m
- dont want the appointment anymore || i,s
- drop my 3pm slot, i wont make it and dont want another one || n,i
- pls cancel my appointment || s,sh
- how do i cancel my visit || q
- i booked by mistake, cancel it || i
- cancel tomorrow's flu shot booking || e
- this is jane doe, cancel my appointment on monday || e
- canceling my appointment, sorry for the short notice || p
- nvm about the appointment, cancel it || s
- i need to cancel the booking i made yesterday || e
- cancle it please, booking 88213 || t,e
#path lab_results
= are my test results ready
= blood report
= Patient is asking about results of lab tests or scans
- are my test results ready || q
- when will i get my blood report || q
- lab results for patient id 55120 || e
- did my xray come back? || q,e
- i gave a blood sample on monday, any update || m,e
- need my cholesterol report || e
- reslts of my urine test pls || t,e
- can you send my reports on whatsapp || i
- has dr patel reviewed my scan results || e
- my thyroid test was done last week, where are the results || m,e
- how long do lab results take || q
- report ready? || s,sh
- i want to see my mri results || e
- got a message saying results are available, how do i view them || i,m
- send my ecg report to my email || e
- waiting for my test report since 5 days || a,e
- still no results?? this is taking forever || a
- my wife's blood work results please, name priya shah || e
- can i get a copy of my lab report || q
- hba1c result for today morning's test || e
- covid test result pls || e,s
- what did my biopsy show || q,e
- report of the sugar test || s
- lab report for booking SF-1207 || e
#path clinic_hours_location
= what time do you open
= where is the clinic
= Opening hours, address or directions to the clinic
- what time do you open || q
- are you open on sunday || q
- wheres the clinic || t,q
- whats your address || q
- closing time today? || s,q
- how do i get to your clinic from the metro station || q,e
- are you open on christmas day || q,e
- opening hours pls || s,sh
- is there parking at the clinic || q
- open now? || sh,q
- which floor is the clinic on || q
- send me the location pin || i
- till what time are you open on saturday || q
- timings? || sh
- is the clinic open on public holidays || q
- do you have a branch near downtown || q,e
- directions please || sh,p
- what are your weekend hours || q
- im outside, which building is it || i,m
- when do you close tonight || q
- google maps link for the clinic? || q
- what time do doors open in the morning || q
- is the clinic near central park || q,e
- lunch break timings? || q
#path talk_to_human
= talk to a person
= connect me to the receptionist
= Customer wants a real staff member instead of the bot
- talk to a person || sh
- i want to speak to a real human || p
- connect me to reception || sh
- can i talk to someone please || p,q
- agent || sh
- this bot is useless, get me a person || a
- call me back please, my number is 9876543210 || e,i
- i need to speak to the receptionist || sh
- human please || sh
- are you a robot? i want a real person || q
- transfer me to staff || sh
- let me talk to the nurse on duty || e
- i've been typing for 10 mins, just connect me to someone || a,m
- customer care || sh
- can a real person help me || q
- operator || sh
- stop the bot, human || a,s
- id like to speak with a staff member please || p
- put me through to somebody || s
- talk to hooman || t,s
- i need someone to call me || i
- live chat with a person? || q
- you dont understand me, let me talk to a human || a
- get me a manager || a
#none
- qwewqeqw || g
- asdfgh || g
- ... || g
- hmm || sh
- ok || sh
- ?? || g
- jkjkjkjk || g
- what's the weather today || o
- write me a poem about cats || o
- who won the football match yesterday || o
- tell me a joke || o
- whats 45 times 12 || o
- lol || s,sh
- do you sell vitamins and supplements || x
- i need a refill of my blood pressure tablets || x
- can you deliver medicine to my house || x
- how much does a full body checkup cost || x
- do you have a vacancy for nurses, i want to apply for a job || x
- my bill is wrong, i was charged twice || x
- can i get a sick leave certificate || x
- zzzzz || g
- k || sh
- best pizza place near me || o
- translate hello to french || o
- sdfkj sdkfj || g
"""

A2 = """
@wf synth3_a_02_medplus_pharmacy
#path refill_prescription
= refill my prescription
= i need more of my medicine
= repeat my last order of tablets
= running out of my pills
= reorder my monthly meds
= refill please
- need a refill for my metformin || e
- refill rx 204551 || e,s
- running low on my bp tablets, can you send more || i
- same order as last month please || i,p
- i'm almost out of my inhaler || i,e
- repeat my prescription for atorvastatin 20mg || e
- refil my meds pls || t,s
- can i get my monthly medicines again || q
- my thyroid pills finish tomorrow, need a new pack || m,e
- reorder my usual || s
- please refill my mother's insulin prescription, name kavita rao || e,p
- i have 2 days of pills left || i
- can you refill my prescription today || q
- set up auto refill for my monthly order || e
- i need more of the antidepressant dr lee prescribed || e
- refill please, same as before || sh,p
- out of my allergy meds again, send another box || i,s
- prescription refill for customer id MP-7781 || e
- my dad needs his heart medicine refilled, he takes it daily || m
- one more month supply of my vitamin d prescription || e
- can u repeat my last order of tablets || s
- refill my eye drops || e
- it's time for my refill || i
- need to top up my diabetes meds before i travel on the 5th || m,e
#path delivery_status
= where is my medicine delivery
= track my order
= when will my meds arrive
= order not delivered yet
= delivery status
- where is my order || q,sh
- my medicines havent arrived yet || i
- track order #77410 || e
- when will my delivery come || q
- ordered yesterday, still waiting || i,m
- the driver said 30 mins, its been 2 hours || a,e
- status of order MP-44102 || e
- is my parcel out for delivery? || q
- still no sign of my meds, i need them today!! || a
- how long till my order reaches || q
- delivery is late again || a
- whats the eta on my insulin order || e,s
- i paid online but nothing delivered yet || i
- wher is my packge || t
- can you check if my order was dispatched || q
- has my order shipped || q
- my tracking link isnt updating || i
- order placed at 9am for my kid's fever medicine, where is it || m,e
- delivery update pls || s,sh
- when do i get my tablets, order 55219 || e
- is someone coming with my medicine today || i,q
- i was told same day delivery, its evening now || a,i
- package status? || sh
- please tell me when my order will arrive, thanks || p
#path check_stock
= do you have paracetamol
= is this medicine available
= in stock?
= do you carry insulin
= check availability of a medicine
- do you have paracetamol 500 || q,e
- is dolo available || q,e
- in stock? amoxicillin || s,e
- do u carry insulin pens || s,e
- do you have covid self test kits || q,e
- is omeprazole 20mg available in your store || e
- looking for vitamin b12 injections, do you have them || e
- any stock of ventolin inhaler || e
- do you sell baby formula || q
- do you keep glucose test strips || q
- is ibuprofen gel in stock || e
- avaialble? cetirizine || t,e
- can i get montelukast from you or is it out of stock || q,e
- i need to know if you have melatonin || i
- does your branch on 5th street have azithromycin || e
- do you stock generic lipitor || e
- checking if you have ors sachets || e
- sunscreen spf 50 available? || e,sh
- is there any stock of nicotine patches || e
- you guys have pregnancy tests? || s,q
- my doctor prescribed levothyroxine 50mcg, do you have it in stock || m,e
- do you have hand sanitizer in stock || e
- before i come in, do you have cough syrup || m,q
- got any ear drops || s
#path transfer_prescription
= move my prescription from another pharmacy
= transfer my prescription to you
= switch pharmacies
= my old pharmacy has my prescription
= get my script from another store
- i want to move my prescription from my old pharmacy to you || sh
- transfer my prescription here || sh
- switching from another pharmacy, how do i get my scripts moved || q,m
- my prescriptions are at citycare pharmacy, can you get them || e
- can you take over my prescriptions from healthmart downtown || e
- i moved to a new city and want to fill my meds with you now || m,i
- how do i transfer an rx || q,s
- tranfer my script pls || t,s
- my previous chemist has my prescription, can you request it || i
- i want to switch pharmacies to medplus || i
- can you call my old pharmacy to transfer my insulin prescription || e
- transfer 3 prescriptions from green cross pharmacy, their number is 555-0142 || e
- i'm done with my current pharmacy, move my meds over to you || a,i
- does transferring a prescription cost anything || q
- my doctor sent my prescription to the wrong pharmacy, can you get it transferred to you || m,i
- please transfer my wife's prescriptions too, name anita das || e,p
- new customer, want to bring over my prescriptions || i
- how long does a prescription transfer take || q
- move my script over from the hospital pharmacy || e
- i'd like my prescriptions transferred to your 5th street branch || e,p
- can i fill my other pharmacy's prescription here || q,i
- switch my rx from store 112 to store 208 || e
- change pharmacy for my prescriptions || sh
#path return_medicine
= return medicine
= wrong medicine delivered
= i want to return my order
= got expired tablets
= damaged package, want a return
- i want to return my order || sh
- got the wrong medicine, want to send it back || m,n
- these tablets are expired, i want a return || a
- the box was damaged when it arrived, i want to return it || m
- return request for order MP-30918 || e
- you sent 10mg instead of 20mg, need to return it || e,n
- can i return unopened medicine || q
- how do i return a product || q
- doctor changed my prescription, can i return the old pack || m,q
- seal was broken on the syrup bottle, taking it back || i
- retrun this pls || t,s
- i ordered 2 boxes by mistake, want to return one || e
- come pick up the wrong item from my home please || i
- this isnt what i ordered, i want to give it back || a,i
- received someone else's medicine, name on it is not mine, want to return it || i
- return policy for unused inhalers? || q,e
- send someone to collect this expired stuff || a,s
- i want to send back the thermometer, it doesnt work || e
- the strips are for a different glucometer, need to return them || e,i
- please arrange a return for my last delivery, thanks || p
- want my money back for the damaged items and return them || e
- return the vitamins i got yesterday || e
- leaking bottle in my order, taking it back || i
- i need to return a medicine i dont need anymore || i
#path thanks_goodbye
= thanks
= thank you
= bye
= that's all
= ok thanks bye
- thanks || sh
- thank you so much || p
- bye || sh
- thats all for now || i
- ok thanks bye || sh
- thx || s,sh
- great, thanks for the help || p
- cheers || s,sh
- got it, thank you || p
- bye bye || sh
- thanks a lot, have a nice day || p
- nothing else, thanks || i
- ty || s,sh
- appreciate it || p
- perfect thanks || sh
- goodbye || sh
- thank u || s
- ok bye || sh
- tysm || s,sh
- thanks, that helped || p
- see ya || s,sh
- thankyou || t
- alright thats it, bye || i
- many thanks || p
#none
- wqeqweqwe || g
- asdf || g
- ..... || g
- hmm || sh
- ??? || g
- lkjhg || g
- what's the capital of australia || o
- write a haiku about rain || o
- how do i cook pasta || o
- bitcoin price today || o
- play some music || o
- hi || sh
- can i book a doctor consultation || x
- is it safe to take ibuprofen with alcohol || x
- what are your store hours || x
- do you offer discounts for seniors || x
- i want to apply for a pharmacist job || x
- how do i update my phone number on my account || x
- what are the side effects of metformin || x
- my card got charged twice || x
- xcvbnm || g
- 🙂🙂🙂 || g
- who is the president of france || o
- tell me something funny || o
- kkkkk || g
"""

A3 = """
@wf synth3_a_03_harbor_dental
#path book_cleaning
= Patient wants to book a routine cleaning, checkup or new dental visit
- i'd like to book a cleaning || p
- need a checkup, havent been to the dentist in 2 years || m
- can i schedule a scaling appointment next week || e,q
- my 6 month cleaning is due, when can i come || i
- book dental checkup for me and my husband || e
- teeth cleaning appt pls || s
- new patient, want a first visit || i
- do you have openings on saturday for a routine checkup || q,e
- i want to get my teeth whitened, can i book a consult || e
- can my kid get a checkup, she is 7 || e
- clening appointment for tuesday || t,e
- book me in with dr morgan for a regular exam || e
- time for my annual dental visit || i
- i want a braces consultation, when are you free || e,q
- schedule a polish and cleaning || sh
- can i get an appointment to review my old filling next month, no pain just routine || e,n
- im due for xrays and a cleaning || i
- booking for a routine visit on 3rd nov, name mark lee || e
- want to come in for a general checkup || sh
- any slot this friday afternoon for cleaning? || q,e
- hey i need a dental cleaning || sh
- can you fit me in for a checkup before christmas || e
- id like to become a patient at harbor dental || i,p
- set up my next hygiene visit || i
#path dental_emergency
= Patient has urgent dental pain, swelling, bleeding or a broken tooth and needs to be seen quickly
- my tooth is killing me, need to see someone today || a,i
- broke my front tooth playing football || m,e
- severe toothache since last night, cant sleep || e
- my gums are bleeding a lot and wont stop || i
- face is swollen on one side, i think its an infection || m,i
- emergency! crown fell off and it hurts || a,e
- wisdom tooth pain unbearable, any emergency slot? || q,e
- my son knocked out a tooth, what do we do || e,q
- i chipped a tooth and the nerve is exposed || e
- urgent dentist needed please || sh
- tooth pain so bad i'm crying || a
- can someone see me right now, my filling fell out and its painful || m,e
- abscess on my gum, really hurts || e
- throbbing pain in my molar, need help asap || s
- the stitches from my extraction are bleeding || e
- toothake emergency || t,sh
- jaw is swelling after my root canal yesterday || e
- i cracked my tooth biting ice, sharp pain || e
- do you take walk in emergencies, im in pain || q,m
- need emergency dental care tonight || e
- my braces wire is stabbing my cheek and it's bleeding || e
- pain when i bite down, it started suddenly and its bad || i
- please help, my tooth is loose and hurts after a fall || p,m
- same day appointment please, extreme tooth pain || n
#path payment_plan
= Patient asks about paying for treatment in installments or monthly payment plans
= Questions about financing options for dental work
- can i pay for my implant in monthly installments || q,e
- do you offer payment plans || q
- the root canal is $1200, can i split it || e
- financing options for braces? || e
- i cant afford it all at once, can i pay in parts || i
- is there a 0% interest plan || q,e
- how does your monthly payment plan work || q
- can i spread the cost over 6 months || e
- do you work with carecredit or similar financing || e
- pay later option for my crowns? || e
- installment plan for my daughter's aligners || e
- i need a payment plan, treatment quote was 3400 || e
- do i need a credit check for financing || q
- what's the minimum down payment for a payment plan || q
- instalments possible? || t,sh
- the treatment is too expensive for me right now, any way to pay slowly || i,m
- can i pay 200 a month || e
- split payment for dentures || s,e
- whats the interest rate on your dental financing || q
- i was quoted for veneers, looking for a monthly plan || e,m
- can i set up automatic monthly payments for my treatment || q
- do you have buy now pay later || q
- i want to finance my wisdom teeth removal || e
- payment plan pls || s,sh
#path cancel_visit
= Patient wants to cancel a scheduled dental appointment
- cancel my appointment || sh
- i need to cancel my cleaning on thursday || e
- please cancel my visit, i'm out of town || p,m
- cancel appt for mark lee on the 3rd || e
- i wont make it tomorrow, cancel it please || i
- can i cancel my dental appointment || q
- no longer need the checkup, cancel || i
- cancel my kid's appointment, booking HD-5521 || e
- cancle my visit || t
- i found another dentist, cancel my booking || i,m
- something came up, please cancel my 9am || e,m
- how do i cancel without a fee || q
- cancel the consult for braces || e
- remove me from tomorrow's schedule || i
- i'd like to cancel my upcoming appointment || p
- dont want the whitening anymore, cancel the booking || s,i
- please call off my appointment on monday || e
- cancel both appointments for me and my husband || e
- sorry, need to cancel my visit this week || p
- my tooth pain went away, cancel the appointment || n,m
- cancel my hygiene visit || sh
- cancel my visit, i'll book later myself || i
- i need to cancel, i'm sick with flu || m
- not coming friday, cancel it || s
#none
- qweqwe || g
- asdasdasd || g
- .. || g
- ok || sh
- hmm || sh
- ...?? || g
- what is the meaning of life || o
- recommend a netflix show || o
- how tall is mount everest || o
- can you move my cleaning to next week instead || x
- what are your opening hours || x
- where is your clinic located || x
- can i get a copy of my dental xrays emailed to me || x
- do you have parking || x
- what toothpaste do you recommend || x
- my bill says i owe 80 dollars, why || x
- hi || sh
- thanks || sh
- jfjfjfjf || g
- write me a cover letter || o
- whats the score in the cricket match || o
- hjkl hjkl || g
- zzz || g
- lol ok || s,sh
- do you have job openings for dental assistants || x
"""

A4 = """
@wf synth3_a_04_lotus_diagnostics
#path home_collection
= home sample collection
= can someone come to my house to take blood
= Customer wants to book a technician to collect samples at home
- book a home blood test for tomorrow 7am || e
- can your technician come to my house || q
- need sample collection at home, address 22 park lane || e
- my father is bedridden, can someone collect his blood at home || m,i
- home visit for thyroid test please || e,p
- send a phlebotomist to my office on friday || e
- i want to book a home collection for lipid profile || e
- can u pick up a urine sample from home || s
- book home collection for 2 people, me and my mom || e
- hme collection tomorow morning || t,e
- id rather not come to the lab, can someone come to me || i
- schedule blood draw at my place, 9876512345 || e
- i need my vitamin d test done at home || e
- can the collection guy come after 6pm || i,e
- book at-home sample pickup for my full body package || e
- im pregnant and cant travel, need home sampling || m,i
- arrange a home visit for my diabetes test on sunday || e
- i want to book home collection in sector 21 || e
- please send someone home for my covid rt pcr || e,p
- doorstep blood test booking || sh
- my kids need blood tests, can someone come home || i
- schedule a technician visit at 8 am tomorrow || e
- book home service for a cbc test || e
- want someone to take my sample at home this week || i
#path report_status
= is my report ready
= Customer asking when or where to get test reports
- is my report ready || q
- when will my cbc report come || q,e
- report for sample id LD-66731 || e
- i gave blood yesterday, where is my report || m,e
- havent received my report on email yet || i
- can you whatsapp me my thyroid report || e
- how long for the lipid report || q,e
- reports not uploaded in the app || i
- still waiting for my report since 3 days, this is ridiculous || a,e
- my doctor needs the results today, is it done || m,i
- download link for my report pls || s
- reprot status || t,sh
- i did the full body package on saturday, results? || m,e
- the report link says expired || i
- my mom's test report, name lakshmi iyer || e
- send me the pdf of my blood test || e
- results of my vitamin d test || e
- how will i get my report || q
- is the hba1c result out || q,e
- can i collect my report from the lab in person || q
- report ready yet?? || a,s
- where can i see my results online || q
- got my urine test done this morning, when are results due || m,e
- did you email the report to dr mehta || e
#path test_price
= how much does a test cost
= price of cbc
= Customer asks the cost of a test or health package
- how much is a cbc test || q,e
- price of thyroid profile || e
- full body checkup cost? || e,sh
- whats the rate for a vitamin d test || q,e
- how much for lipid profile and hba1c together || e
- cost of covid rt pcr || e
- do you have any cheap health packages || q
- price list please || p,sh
- how much does a diabetes panel cost || q
- is there a discount on the senior citizen package || q,e
- charges for a liver function test || e
- wat is the price of urine routine test || t,e
- how much will it cost for my whole family's checkup, 4 people || e
- rate card for blood tests || s
- how expensive is an allergy panel || q
- vit b12 test how much || s,e
- what does the womens health package cost || e
- cheapest thyroid test you have? || q
- kidney function test price || e
- can you tell me the fee for an iron studies test || p,e
- how much for a pregnancy blood test || e
- total cost for cbc, esr and crp || e
- is the heart checkup package under $100 || e
- pricing for fasting blood sugar || e
#path test_preparation
= do i need to fast
= Customer asks how to prepare before a test, like fasting or stopping medicine
- do i need to fast before a lipid test || q,e
- how many hours fasting for blood sugar || q
- can i drink water before my blood test || q
- should i stop my bp medicine before the test || q,e
- any preparation needed for thyroid test || q,e
- can i have coffee before the sample collection tomorrow || q,e
- fasting required for full body checkup? || e
- i'm diabetic, should i take insulin before the fasting test || m,e
- what to do before a urine test || q
- can i eat breakfast before my cbc || q,e
- is 8 hours fasting enough || q,e
- do i need to avoid alcohol before a liver test || q,e
- instructions for glucose tolerance test || e
- ok so my test is at 7am, can i eat dinner late the night before || m,e
- shud i fast for vitamin d test || t,s
- can i brush my teeth before the blood test || q
- do i need to stop my vitamins before testing || q
- how to prepare for a stool test || q
- is it ok to smoke before the test || q
- my son is 5, does he also need to fast || e,m
- any diet restrictions before hba1c || e
- i had a snack by mistake, is it fine for the fasting test || i,m
- what should i do the night before my test || q
- can i take my thyroid pill before the test in the morning || q,e
#path talk_to_human
= talk to an agent
= call me
= Customer wants to speak to a person
- talk to an agent || sh
- call me please || p,sh
- i want to speak to someone || sh
- connect me to customer support || sh
- please have someone call me at 9123456780 || e,p
- real person please || sh
- this is confusing, i need a human || a
- can i talk to your lab staff || q
- put me on call with someone || s
- need a callback || sh
- agent pls || s,sh
- im tired of this bot, human now || a
- can someone from lotus call me back today || e,q
- i want to speak to the manager about my experience || a,e
- connect me to a live agent || sh
- talk to a rep || s
- is there a helpline number i can call || q
- hellooo anyone real there? || q
- speak with somebody please || p
- need to talk to a person urgently || a
- transfer to human agent || sh
- customer care number? || q
- ring me back when free || s,i
- let me chat with an actual person || i
#none
- asdfasdf || g
- qwqwqwqw || g
- ... || g
- hmm || sh
- ok || sh
- ??? || g
- xyzzy || g
- what's the weather in london || o
- write me a love poem || o
- how to lose weight fast || o
- cancel my home collection booking || x
- do you have a branch in austin || x
- my payment failed while booking || x
- can i get a doctor consultation || x
- do you hire phlebotomists || x
- what's the stock price of tesla || o
- tell me a joke || o
- k || sh
- lol || s,sh
- jkljkl || g
- hi || sh
- thanks || sh
- who invented the telephone || o
- mnbvcx || g
- what is your refund policy for cancelled tests || x
"""

A5 = """
@wf synth3_a_05_northside_hospital
#path greeting
= hi
= hello
= good morning
= hey
- hi || sh
- hello || sh
- hey || sh
- good morning || p,sh
- good evening || p,sh
- hiya || s,sh
- hello there || sh
- hii || t,sh
- morning || sh
- hi northside || sh
- hey team || sh
- good afternoon || p,sh
- helloo || t,sh
- hi hi || sh
- gm || s,sh
- hey good morning || sh
- greetings || p,sh
- hi 🙂 || sh
- howdy || s,sh
- hello hospital || sh
- hey there || sh
- good day || p,sh
#path book_appointment
= book appointment
= see a doctor
= consult a specialist
= new appointment
= schedule opd visit
- i want to see a cardiologist next week || e
- book opd appointment with dr fernandes || e
- need to consult an orthopedic doctor for my knee || e
- appointment for my daughter with a pediatrician on monday || e
- can i get a slot with a neurologist || q,e
- schedule a visit for my annual physical || e
- book appointmnt with ent || t,e
- need a gynecologist appointment asap || s,e
- my mom needs to see a doctor for her diabetes, can i book || m,e
- first time here, how do i book a consultation || q
- earliest slot with dermatology? || q,e
- i'd like an appointment with dr ahmed please || p,e
- book me for tomorrow morning, general medicine || e
- want to see a specialist about my migraines || e
- can you book a follow up after my surgery last month || m,e
- eye checkup appointment pls || s,e
- need to meet a psychiatrist, is saturday possible || q,e
- book a slot for 4pm today || e
- i keep getting stomach aches for weeks, want to see a gastro doctor || m,e
- new appointment for patient id NH-20931 || e
- wanna book a doctor || s
- any doctor free this evening for a consultation? || q
#path cancel_appointment
= cancel appointment
= cancel my booking
= i can't come, cancel
- cancel my appointment || sh
- cancel appointment NH-20931 || e
- i can't come tomorrow, cancel it || i
- please cancel my visit with dr fernandes || p,e
- cancel the cardiology booking for friday || e
- no need for the appointment anymore || i
- cancel my mom's appointment, she's feeling better || m
- cancell my opd slot || t
- i booked twice by mistake, cancel one || e,i
- how do i cancel a booking || q
- drop my appointment on the 18th || e
- cancel all my upcoming appointments || e
- i want to cancel, not change the date || n
- we're shifting cities, please cancel my son's appointment || m,e
- cancel booking for 4pm || e
- pls cancel my eye checkup || s,e
- cancel it, i'll go to another hospital || i,a
- remove my name from tomorrow's appointments || i
- my surgery follow up needs to be cancelled || e
- cant make it, cancel || s,sh
- cancel the booking i made this morning || e
- i would like to cancel my consultation || p
#path visiting_hours
= visiting hours
= when can i visit a patient
= ward visiting time
= can family visit
- what are the visiting hours || q
- can i visit my father in the icu || q,e
- when can family visit in ward 5 || e
- visiting time today? || sh
- is visiting allowed on sundays || q
- how many visitors are allowed per patient || q
- my wife is admitted in room 304, when can i see her || m,e
- can kids visit patients || q
- visitng hrs for maternity ward || t,e
- till what time can i stay with my mom in the ward || q
- evening visiting time? || sh
- can i bring food when visiting a patient || q
- is night stay allowed for attendants? || q
- my friend had surgery yesterday, can i go see him || m,i
- visitor pass how to get || s,q
- what time does visiting end || q
- any rules for visitors right now? || q
- can i visit someone in the isolation ward || q
- my grandma is in general ward, visiting hours pls || e,s
- can two people visit at once || q
- is there a visiting slot in the morning || q
- when can i meet my brother, he's admitted in bed 12 || e,i
#path medical_records
= get my medical records
= discharge summary copy
= need my old reports
= request records
- i need a copy of my medical records || sh
- discharge summary please || sh
- can you email my old reports from 2022 || e
- need my full medical history for a second opinion || i
- how do i get my records transferred to another hospital || q
- requesting my mri images on cd || e
- my patient id is NH-55012, need all my files || e
- send me my father's discharge papers, he was admitted last month || m,e
- copy of my surgery notes || e
- need my vaccination records for school admission || e
- can i get my son's birth records from your hospital || e
- lost my discharge summary, need another copy || m,i
- medical recrods request || t
- where do i apply for my medical file || q
- i want my xray films from last year || e
- doctor asked for my previous prescriptions from your hospital || i
- can i collect my old reports in person || q
- please share my treatment history with dr lim at city clinic || p,e
- need certified copies of my records for court || e
- how long does a records request take || q
- my mom passed away here, i need her records || m,e
- can i download my health records online? || q
#path bill_payment
= pay my bill
= hospital bill
= how to pay
= outstanding amount
- how do i pay my bill || q
- pay hospital bill online || sh
- what's my outstanding amount || q
- i want to pay the bill for patient NH-44120 || e
- can i pay by credit card at the counter || q
- bill for my discharge is 42,500, can i pay in two parts || e
- send me the payment link || i
- how much do i owe || q
- pay my father's hospital charges || e
- bil payment || t,sh
- i paid but it still shows due || a,i
- do you accept bank transfer || q
- need an itemized bill || e
- why is my bill so high, 3 nights cost 900 dollars?? || a,e
- where do i pay before discharge || q
- pending payment for my surgery, how to clear it || e
- paying for my mom's treatment, whats the amount || e
- receipt for my payment yesterday || e
- can i pay the deposit for admission here || q,e
- want to settle my bill today || i
- payment failed on the website, tried 3 times || m,a
- send me the invoice for my opd visit || e
#path pharmacy_refill
= refill prescription
= need medicine refill
= hospital pharmacy refill
- refill my prescription || sh
- need my blood pressure medicine refilled || e
- can the hospital pharmacy refill my insulin || q,e
- my discharge medicines are almost finished || i
- refill rx for patient NH-20931 || e
- running out of my heart pills, need more || i
- same medicines as last month please || i,p
- refil my inhaler || t,e
- can i get a refill without seeing the doctor again || q
- my dad's seizure medication needs a refill || e
- repeat prescription for my thyroid tablets || e
- monthly refill of my diabetes meds || e
- i only have 3 days of pills left || i,e
- can you have my meds ready for pickup at the pharmacy || i
- refill order for metoprolol 50mg || e
- need more of the painkillers dr ahmed gave me || e
- reorder my medicines from last visit || i
- pls refill my mom's prescription, name rose thomas || e,s
- can i get a 3 month refill || q,e
- need refills for my post surgery meds || e
- refill my cholesterol pills || e
- is my refill ready || q
#path emergency
= emergency
= ambulance
= chest pain
= someone collapsed
= urgent help
- emergency || sh
- need an ambulance now || a
- my father has chest pain and is sweating || m,e
- someone collapsed at home, please help || a,m
- my child is not breathing properly || a
- send ambulance to 14 river road || e
- car accident, my friend is bleeding a lot || m,a
- my wife is in labour, we need help now || e,a
- he's having a seizure what do i do || a,q
- emergncy please help || t,a
- severe allergic reaction, face swelling up || e
- my mom fainted and isnt waking up || a
- urgent, ambulance to main street near the mall || e
- i think i'm having a stroke, my arm is numb || m
- chest pain since 20 mins, is the er open || q,e
- my son swallowed something and is choking || a
- heavy bleeding after delivery, need help || e
- fell from the stairs, cant move my leg, need ambulance || m
- i feel like i might hurt myself, please help || i
- difficulty breathing, asthma attack || e
- high fever and fits in my baby || e,a
- where is the emergency room entrance || q
#path goodbye
= bye
= thanks
= thank you
= that's all
- bye || sh
- thanks || sh
- thank you || sh
- thats all || sh
- thanks bye || sh
- thank u so much || s
- ok thanks || sh
- goodbye || sh
- cya || s,sh
- tysm || s,sh
- thanks for your help || p
- great thank you || p
- bye bye || sh
- many thanks || p
- that's it for today || i
- appreciate the help || p
- nothing more thanks || i
- thx bye || s
- have a good day || p
- done, thank you || i
- ok bye || sh
- thankss || t
- cheers mate || s
#none
- qwewqeqw || g
- asdfjkl || g
- ... || g
- hmm || sh
- ??? || g
- lkjlkj || g
- zxcvb || g
- what's the weather tomorrow || o
- write me a poem || o
- who won the world cup || o
- best laptop under 500 || o
- how to make pancakes || o
- is the parking free at the hospital || x
- do you have job vacancies for nurses || x
- i want to give feedback about a nurse || x
- can i reschedule my appointment to next week || x
- how much does an mri cost || x
- what are the opd timings for dr ahmed || x
- do you have a cafeteria || x
- is there wifi in the hospital || x
- jjjjjj || g
- lol || s,sh
- tell me a joke || o
- translate this to spanish || o
- 🤔 || g
- the the the || g
- k || sh
"""

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    write([A1, A2, A3, A4, A5], "healthcare_clinic_pharmacy", "synth_3_hand_authored",
          os.path.join(root, "data/synthetic/synth_3_a.jsonl"))
