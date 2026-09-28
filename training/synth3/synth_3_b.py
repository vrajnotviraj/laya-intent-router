"""Synthetic training workflows: SaaS / IT helpdesk / software support. Run: python training/synth3/synth_3_b.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import write

B1 = """
@wf synth3_b_01_flowbase_saas
#path reset_password
= forgot password
= reset my password
= User cannot remember their password and wants to reset it
- forgot my password || sh
- how do i reset my password || q
- i cant remember my password for flowbase || i
- password reset link not received || i
- reset pwd for john@acme.com || e,s
- i need a new password || sh
- forgot password, the email is maria.g@outlook.com || e
- reset password pls || s,sh
- change my password, i think someone knows it || m,i
- the reset email went to spam and expired, send another || m,i
- fogot pasword || t
- how to change password in settings || q
- i lost my password || i
- my password isnt working, i think i forgot it || i,n
- can u send me a password reset email || s,q
- new phone, dont remember my login password || m,i
- reset the password for my team member sam, he forgot it || e
- need to set a new password for workspace acme-prod || e
- i must have forgotten my password, how do i reset it || m,n
- where is the forgot password button || q
- update my password please || p
- resetting password isnt obvious, help || i
- password recovery || sh
- i forgot my password and the security question answer too || m
#path account_locked
= my account is locked
= locked out after too many attempts
= User's account is locked, suspended or disabled and they cannot get in even with the right password
- my account is locked || sh
- locked out after too many login attempts || n
- it says account suspended, why || q,a
- account disabled message when i log in || i
- i typed the right password but it says my account is locked || m,n
- unlock my account please, user id FB-40913 || e,p
- your system locked me out, i have a demo in 1 hour || a,m
- account locked after 5 attempts, how long do i wait || q,e
- my admin says my account got deactivated, can you reactivate it || m,i
- acount blocked?? || t,a
- i'm locked out of my workspace || i
- why was my account suspended, i paid my bill || a,m
- it says too many failed attempts, try again later. i need access now || m,a
- unlock user ravi@acme.io || e
- my login is blocked even after resetting password || n
- suspended account appeal || sh
- our whole team got locked out this morning || e,i
- my account got flagged and frozen || i
- the security lock kicked me out and wont let me back in || i
- account deactivated by mistake, restore it || i
- it says your account has been disabled contact support || i
- can you unlock my account || q
- locked for 30 mins now, still cant get in || a,e
- i got a temporary lock email, what do i do || q
#path billing_invoice
= download invoice
= billing question
= User wants an invoice, receipt or has a question about a charge
- where can i download my invoice || q
- need the invoice for march || e
- why was i charged $49 twice || a,e
- send me a receipt for my last payment || e
- i need an invoice with our company vat number || e
- billing question about my latest charge || sh
- what is this $12 charge on my card from flowbase || e,q
- invoice #INV-20931 has the wrong address || e
- add our tax id to the invoices || e
- charged after trial ended, i didnt expect that || i,a
- invoices for the last 12 months please || e,p
- my card was charged but plan shows unpaid || i
- change billing email to finance@acme.com || e
- need a pro forma invoice to get approval || e
- where do i see my billing history || q
- invoce for feb pls || t,s
- can i get a receipt in euros || q,e
- you overcharged me this month || a
- update the company name on my invoices || i
- payment failed, how do i update my card || q
- what's the next billing date || q
- how much am i paying per seat right now || q
- i need a copy of the receipt for expense reimbursement || i
- double charge on my account, order FB-8812 || e,a
#path cancel_subscription
= cancel my subscription
= stop auto renewal
= User wants to end their paid plan
- cancel my subscription || sh
- i want to stop auto renewal || sh
- how do i cancel my plan || q
- please cancel our pro plan at the end of this month || p,e
- we're moving to another tool, cancel our subscription || m,i
- turn off auto renew || sh
- dont charge me again, i want to cancel || a,n
- cancel subscription for workspace acme-prod || e
- cancle my plan || t
- i no longer need flowbase, end my subscription || i
- stop my monthly payments and close the plan || i
- we're a small team now, not using it, cancel it || m,i
- can i cancel anytime without a fee || q
- unsubscribe me from the paid plan || s
- cancel my trial before it charges me || e,n
- end my annual subscription please || p
- how to cancel the business plan || q,e
- i want to cancel, what happens to my data || q,m
- cancel before renewal on 1st october || e
- this is too expensive, cancel it || a
- stop billing me and cancel my plan || a,n
- cancel our seats and subscription entirely || e
- im done, cancel everything || a,s
- cancel my subscription asap || s
#path upgrade_plan
= upgrade to pro
= add more seats
= User wants to move to a higher plan or buy more capacity
- upgrade to pro || sh
- i want to add 5 more seats || e
- how do i move to the business plan || q,e
- we need more storage, can i upgrade || i
- upgrade my plan please || p,sh
- buy extra seats for my team || sh
- going from starter to pro, how much || e,q
- we hired 3 new people, need seats for them || m,e
- upgrade workspace acme-prod to enterprise || e
- upgarde pls || t,s
- increase our user limit to 50 || e
- hit the project limit, want to upgrade || i
- what do i get if i go premium || q
- we want the enterprise tier || e
- add more api calls to our plan || e
- upgrade trial to paid || e
- can i upgrade mid month || q
- need more seats asap, launch is on monday || m,e,s
- unlock the pro features for my account || n
- i want the bigger plan || s
- upgrade from 10 to 25 users || e
- how do i get more storage space || q,i
- go premium || sh
- our team outgrew the free plan || i
#path report_bug
= something is broken
= app is crashing
= User reports an error, bug or feature not working
- the app keeps crashing when i open a board || e
- something is broken, i cant save tasks || i
- getting error 500 on the dashboard || e
- export button does nothing || i
- bug: notifications arent sending || e
- page wont load since the last update || i
- the mobile app freezes on the home screen || n
- drag and drop stopped working in chrome || e
- i found a bug in the calendar view, dates are off by one day || e,m
- the search is showing wrong results || i
- attachments over 5mb fail to upload || e
- error code FB-ERR-212 when i click share || e
- sync between desktop and mobile is broken || i
- its super slow today, takes 30 seconds to load a page || a,e
- the comment box disappears when i type || i
- aplication crash after update || t
- integrations page shows a blank screen || i
- the create project button gives an error || e
- dark mode makes text invisible on reports || e
- emails from the app are coming in blank || i
- your latest release broke our workflow automations || a
- the timer feature isnt counting properly || i
- charts are not rendering in safari || e
- screen goes white when i open settings || i
#path talk_to_human
= talk to support agent
= Customer wants a human
- talk to support agent || sh
- can i speak to a human || q
- connect me to a real person || sh
- i want a live agent || sh
- your bot isnt helping, get me someone || a
- support team please || sh,p
- agent || sh
- human || sh
- i need to talk to someone from your team || i
- call me at +1 415 555 0199 || e
- schedule a call with support || i
- put me through to tech support staff || s
- can a person look at my issue || q
- escalate this to a human || a
- i want to chat with a real support rep || s
- talk to my customer success manager || e
- is there anyone i can talk to? || q
- please connect me with an engineer || p
- speak to someone now || a
- live chat pls || s,sh
- hooman agent || t,s
- i'd prefer talking to a person, thanks || p
- get me support staff on the line || s
- transfer me to your team || sh
#none
- qwerty123 || g
- asdfg || g
- ... || g
- hmm || sh
- ok || sh
- ?! || g
- lolol || s,sh
- what's the weather like today || o
- write me a poem about the sea || o
- what's a good laptop for gaming || o
- how do i make cold brew coffee || o
- who is the richest person alive || o
- can you add a gantt chart feature || x
- how do i invite a teammate || x
- export my data to csv || x
- do you have a mobile app || x
- is my data stored in the eu || x
- change my profile photo || x
- do you integrate with slack || x
- jfkdlsa || g
- sdf sdf sdf || g
- hi || sh
- thanks || sh
- tell me a riddle || o
- mmmmm || g
"""

B2 = """
@wf synth3_b_02_internal_it_helpdesk
#path vpn_issue
= vpn not working
= cant connect to vpn
= vpn keeps disconnecting
= vpn error
= remote access down
- vpn not connecting from home || i
- anyconnect says connection attempt failed || e
- vpn keeps dropping every 10 mins || e,a
- cant reach internal sites when working remote || i
- vpn error 809 || e
- my vpn password expired, now i cant connect || m
- remote access is down for me || sh
- vpn super slow today || s
- connected to vpn but cant open the intranet || m,i
- vpm not working || t
- wfh and vpn wont log in || s
- the vpn client crashed after the update || e
- vpn authentication failed, tried 3 times || e,a
- is the vpn down for everyone? || q
- cant access the file server from home, vpn issue i think || m,i
- vpn stuck on connecting || i
- vpn disconnects when i join a video call || i
- im in the hotel and vpn wont connect || i,m
- globalprotect not connecting || e
- urgent: vpn broke 5 min before my client call || a,e
- vpn shows certificate error || e
- remote desktop through vpn times out || e
- my vpn token isnt accepted || i
- vpn issue again!! || a,sh
#path new_hardware
= need a new laptop
= request a monitor
= my laptop is old, replace it
= order a keyboard and mouse
= hardware request
- need a new laptop || sh
- my laptop is 5 years old and super slow, can i get a replacement || m,e
- request a second monitor || e
- can i get a new keyboard, keys are broken || e,i
- need a headset for calls || e
- new joiner starting monday needs a laptop, name tom baker || e,m
- my laptop screen cracked, need a new one || i
- order a docking station for me || e
- can i get a macbook instead of windows laptop || q,e
- battery dead on my laptop, replacement please || i,p
- need a webcam for meetings || e
- request an ergonomic mouse || e
- my mouse stopped working, need another || i
- hardware request for 3 monitors for the design team || e
- lapttop replacement || t
- can i get a bigger monitor || q
- i need a work tablet for site visits || e
- my charger is lost, need a new one || i,e
- the keyboard i got is faulty, need a replacement || i
- upgrade my laptop ram to 32gb || e
- new hire kit: laptop, mouse, headset for anna from sales || e
- need usb c adapter || s,e
- can you send me a spare laptop while mine is in repair || e
- my laptop wont turn on at all, need a loaner || i,m
#path software_install
= install software
= need photoshop
= can you install zoom
= software request
= need a license for an app
- install zoom on my laptop || e
- i need photoshop for a project || e
- can you install python and vscode || e,q
- need a license for adobe acrobat pro || e
- software request: tableau desktop || e
- please install microsoft teams, its missing || e,p
- how do i get slack installed on my machine || q,e
- need autocad for the new engineering project || e
- can i get figma desktop app || q,e
- instal chrome please || t,e
- my visio license expired, need it renewed || e
- i need notepad++ on my laptop || e
- request to install docker desktop || e
- can someone install the new version of excel for me || e
- put spss on my pc for the stats course || e,s
- missing software after laptop reimage, need office installed || m,e
- please upgrade my windows to 11 || e
- install java 17 please || e
- where do i request new software || q
- need a pdf editor installed || e
- can i get 1password installed || e
- my team needs postman on our laptops || e
- install the latest teams update for me || e
- need a license key for sketch || e
#path email_issue
= email not working
= outlook not syncing
= cant send emails
= not receiving emails
= mailbox full
- outlook not syncing on my laptop || e
- i cant send emails since morning || i
- not receiving any emails from clients || i
- mailbox full error || e
- emails stuck in outbox || i
- my email password isnt working on my phone app || e
- outlook keeps asking for password || e
- i'm getting a bounce back on every email || i
- email not working on my iphone || e
- calendar invites not showing in outlook || e
- my inbox is empty, all emails disappeared || a,i
- emial not loading || t
- cant attach files larger than 10mb || e
- outlook crashes when i open an email || e
- external people say my emails go to spam || i
- my email signature disappeared || i
- out of office reply isnt working || i
- emails from hr@company.com not coming through || e
- getting "cannot connect to server" in mail app || e
- im not getting any new mail since yesterday 4pm || e,i
- outlook search not finding old emails || e
- sent emails arent saving in sent folder || i
- email is super slow to load || s
- urgent, my email is down and i have a deadline || a,m
#path printer_problem
= printer not working
= cant print
= printer jammed
= add a printer
= printer offline
- printer not working || sh
- cant print anything today || i
- printer on 3rd floor is jammed || e
- my print jobs are stuck in queue || i
- how do i add the new printer to my laptop || q
- printer offline again || a
- printer says out of toner || e
- prints are coming out blank || i
- cant scan to email from the copier || e
- printr jammed again ugh || t,a
- the hr printer is printing random symbols || i
- need to print in color but only b&w works || i
- my laptop cant find the printer || i
- printer driver error || e
- paper jam on the printer near reception || e
- printing takes forever || s
- set up printing on my new mac || e
- the badge release printer isnt picking up my job || e
- double sided printing not working || e
- printer showing error E-04 || e
- cant print pdfs, word docs print fine || m,e
- who fixes the printer in meeting room b || q,e
- printer keeps printing the same page || i
- printing is broken on floor 2 || e
#path access_request
= need access to a shared drive
= give me access to jira
= permission request
= add me to a group
= access denied on folder
- need access to the finance shared drive || e
- give me access to jira || e
- access denied on the marketing folder || e
- add me to the engineering group || e
- can i get edit rights on the budget spreadsheet || q,e
- new joiner needs access to salesforce and confluence, name priya || e
- i need admin rights on my laptop || i
- please grant me read access to the hr sharepoint || p,e
- add me to the #devops slack channel || e
- permission request for github repo payments-api || e
- i get "you dont have permission" opening the dashboard || i
- my access to the crm was removed, need it back || i
- access to the production database for my project || e
- can my manager approve access to the design folder || q
- i moved teams, need access to the ops drive || m,e
- add me to the qa team in azure devops || e
- cant open the shared folder, says request access || i
- acess to tableau server pls || t,s
- remove my old access and give me the new team's permissions || e
- need temporary access to the vendor portal for 2 weeks || e
- contractor needs access to our wiki, email ext.jake@vendor.com || e
- how do i request access to a system || q
- i can see the folder but cant edit files || i
- share drive permissions for me || s
#none
- qwewqeqw || g
- asdkjasd || g
- ... || g
- hmm || sh
- ok || sh
- ??? || g
- what's for lunch today || o
- will it rain tomorrow || o
- write a poem about mondays || o
- when is the next public holiday || o
- how do i apply for leave || x
- my salary is wrong this month || x
- reset my windows login password || x
- the wifi in the office is down || x
- the aircon in meeting room 3 is too cold || x
- is there an ev charging station in the parking || o
- book a meeting room for 3pm || x
- who is the ceo of google || o
- tell me a joke || o
- lol || s,sh
- xxxxx || g
- hi || sh
- thanks || sh
- bye || sh
- sdfsdf || g
- ughhhh || sh
"""

B3 = """
@wf synth3_b_03_paylane_payroll
#path add_employee
= Customer wants to add or onboard a new employee to payroll
- how do i add a new hire to payroll || q
- we hired someone, starts on the 1st, how do i set him up || m,e
- add employee jane smith to payroll || e
- onboard 3 new staff this month || e
- need to add a contractor to paylane || e
- where do i enter a new employee's details || q
- new joiner, salary 65k, how to add || e
- adding a part time worker, what info do you need || q
- i cant find the add employee button || i
- ad new emplyee || t
- we're hiring 10 seasonal workers, can i bulk add them || m,e
- set up payroll for our first employee || e
- how to invite a new employee to fill their own details || q
- add my new office manager to next payroll run || e
- new starter paperwork, how do i get them on payroll || i
- can i add an employee who starts mid month || q
- enroll a new worker based in california || e
- onboarding a remote employee in texas, steps? || e
- need to put a new intern on payroll, stipend 1500 || e
- my new hire needs to get paid this month, how do i add them || i
- import new employees from a spreadsheet || e
- add someone to payroll please || p
- hi, we just hired a cook for our restaurant, how do we add him || m
- register new employee id EMP-2231 || e
#path payroll_failed
= Payroll run failed, was delayed or employees were not paid correctly
- payroll failed this morning || sh
- my employees didnt get paid today || a,i
- payroll run shows error, nobody got their salary || m,a
- payday was friday and money still hasnt arrived || i,e
- payroll stuck in processing since yesterday || e
- two employees got paid twice || e
- why was payroll delayed || q
- salary for march not credited to staff || e
- error "funding failed" when running payroll || e
- wrong amount paid to sarah, she got 1200 instead of 2100 || e
- payrol didnt go through || t
- urgent! 40 people waiting on salary, run failed || a,e
- my paycheck is missing this week || i
- the payroll run got cancelled automatically, why || q
- overtime wasnt included in this payroll || i
- direct deposits bounced for half the team || e
- run id PR-7781 failed, need help || e
- employees are complaining they got paid less || i,a
- payroll was supposed to go out at 9am, its 3pm || a,e
- too much tax was withheld in this payroll run || n
- bonus payments not processed || e
- our payroll is late again, this is the second time || a
- some staff got paid but others didnt || i
- payroll approval went through but money not sent || m
#path tax_forms
= Customer needs tax documents like W-2, 1099 or year end tax forms
- where do i download w-2s || q,e
- need 1099 forms for my contractors || e
- year end tax forms for 2025 || e
- my employee lost her w2, can i get another copy || m,e
- when will w-2s be available || q
- how do i file 1099-nec through paylane || q,e
- send me my w2 || s,e
- tax documents for last year please || p,e
- corrected w-2 needed, name was misspelled || e,m
- can employees download their own tax forms || q
- where are the quarterly 941 filings || e
- w2 not showing in portal || i,e
- need form 940 copy || e
- tax fomrs download || t
- state tax forms for new york employees || e
- i need proof of tax filed for my loan application || i
- generate 1099s for 12 contractors || e
- former employee asking for his w-2, he left in june || m,e
- can i get the tax summary report for the year || q
- annual tax statement for my records || e
- is the w2 mailed or emailed || q
- our accountant needs all tax filings from paylane || i
- 1099-misc copies please || e
- download year end tax reports || sh
#path update_bank_details
= Customer wants to change the company or an employee's bank account details
- change our company bank account || sh
- employee changed banks, need to update his account number || m,e
- update direct deposit info for maria lopez || e
- new bank details for payroll funding account || e
- how do i change the bank account salaries are paid from || q
- i switched banks, update my direct deposit || i
- wrong routing number entered for john, fix it || e
- update bank for employee EMP-1043 || e
- we moved business banking to a new bank, what do i do in paylane || m,q
- change acount details || t
- can employees update their own bank info || q
- i need to add a second bank account for split deposit || e
- my employee closed her old account, next pay must go to the new one || m,i
- edit bank account for contractor || sh
- new iban for our uk employee || e
- update payroll funding account before next run || e
- how to verify a new bank account || q
- bank details changed, account ending 4421 || e
- switch the debit account for payroll to our new chase account || e
- please update the account number, the old one is closed || p,i
- i need to change where my salary goes || i
- correct the bank info, typo in account number || e
- change my bank || sh
- update company bank before the 25th || e
#none
- qwewq || g
- asdfasd || g
- .. || g
- ok || sh
- hmm || sh
- ??? || g
- what's the weather in chicago || o
- write a poem about spring || o
- tell me a joke || o
- how do i give an employee a raise || x
- how do i terminate an employee || x
- how many vacation days does my employee have left || x
- change my login email || x
- cancel my paylane subscription || x
- do you support payroll in canada || x
- how do i set up health benefits for staff || x
- what's the minimum wage in texas || o
- jkjk || g
- hi || sh
- thanks || sh
- lol || s,sh
- who is the richest man in the world || o
- recipe for pancakes || o
- bnmbnm || g
- qqqq || g
"""

B4 = """
@wf synth3_b_04_hostnest_hosting
#path greeting
= hi
= hello
= User says hello
- hi || sh
- hello || sh
- hey || sh
- hey there || sh
- good morning || p,sh
- hii || t,sh
- hello hostnest || sh
- hi team || sh
- morning || sh
- yo || s,sh
- helo || t,sh
- good evening || p,sh
- hey hey || s,sh
- hi! || sh
- hello?? || sh
- gm || s,sh
- hi there || sh
- good afternoon || p,sh
- heyy || t,sh
- hey folks || s,sh
- hiya || s,sh
- greetings || p,sh
#path website_down
= my site is down
= website not loading
= User reports their hosted website is offline or showing errors
- my site is down || sh
- website not loading since 2am || e
- getting 503 error on mysite.com || e
- my wordpress site shows a white screen || e
- is there an outage? all my sites are offline || q,a
- error establishing database connection on my blog || e
- site down, losing customers every minute!! || a
- www.bakerybliss.com isnt opening || e
- my website takes forever and then times out || i
- server not responding, account HN-4471 || e
- webiste down again || t,a
- customers say they cant reach my shop online || i
- 500 internal server error after i updated plugins || m,e
- my site is showing your default page instead of my content || i
- dns not resolving for my site, it wont open || e
- the site works for me but my clients see an error || i
- cpanel says my account is suspended and the site is offline || i
- my online store has been down for 3 hours || e,a
- 502 bad gateway || e,sh
- hosting down? || s,sh
- my homepage is blank since yesterday || e
- the site crashed after the traffic spike from our sale || m
- cant access my website or admin panel || i
- website unreachable, please check the server || p
#path domain_renewal
= renew my domain
= domain expiring
= User wants to renew or extend a domain registration
- renew my domain || sh
- my domain expires next week, how do i renew || m,e
- renew bakerybliss.com for 2 years || e
- got an email that my domain is expiring || i
- extend domain registration || sh
- domain renewl || t
- can i set my domain to auto renew || q
- my domain expired yesterday, can i still get it back || m,e
- how much is it to renew a .com || q,e
- renew all 3 of my domains || e
- please renew example.org before it lapses || p,e
- i want to keep my domain for another year || i
- domain renewal for account HN-2290 || e
- dont let my domain expire, renew it || a,i
- is my domain renewal due soon || q
- renew the .co.uk domain too || e
- my domain is in grace period, renew asap || e,s
- card declined when renewing my domain || i
- can i renew for 5 years at once || q,e
- extend my domain before 30 nov || e
- renew domain + privacy protection || e
- keep mydomain.net active for next year || e
- reminder says domain expiring in 3 days, renew pls || e,s
- how do i renew my domain name || q
#path ssl_certificate
= ssl not working
= install https certificate
= User has problems with or wants an SSL/HTTPS certificate
- ssl not working on my site || sh
- browser says not secure on my website || i
- install an ssl certificate for shop.example.com || e
- my https certificate expired || e,n
- how do i get a free ssl || q
- getting "your connection is not private" error || n
- enable https on my domain || e
- renew my ssl certificate || n
- mixed content warning after adding ssl || e
- lets encrypt certificate failed to install || e
- padlock is missing on my site || i
- ssl for subdomain blog.mysite.com || e
- certificate mismatch error on www || e
- wildcard ssl price? || q,e
- my ssl says invalid || i
- ssl cert expred || t
- customers see a security warning when checking out || i,m
- force http to https redirect || e
- upload my own ssl certificate from another provider || e
- do you offer ev ssl certificates || q,e
- ssl stopped working after i changed dns || m
- need https for my online store before launch || e
- certificate error on my webmail || e
- ssl pls || s,sh
#path refund_status
= where is my refund
= User already requested a refund and wants to know its status
- where is my refund || q,sh
- i requested a refund 10 days ago, still nothing || m,a
- refund status for ticket HN-9981 || e
- you approved my refund but money hasnt reached my card || m,i
- when will i get my money back, already applied last week || n,m
- how long do refunds take to show || q
- my refund of $89 is pending || e
- still waiting on the refund you promised || a,i
- any update on my refund request? || q,n
- refund not received yet || i
- got an email saying refund processed, but bank shows nothing || m,i
- check the status of my refund please || p
- refnd status? || t,sh
- its been 3 weeks since my refund was approved || a,e
- did you process my refund for the vps plan || q,e
- my refund was supposed to arrive by friday || e,i
- has my money been sent back? || q
- refund reference RF-20331, where is it || e
- you said 5-7 days for the refund, its day 10 || a,e
- following up on the refund i asked for || n
- is my refund on its way || q
- refund went to which card? i dont see it || m,q
- refund was confirmed on chat yesterday, when will it show || m,e
- still no refund lol || s,a
#path refund_request
= i want a refund
= User wants to ask for money back for a service
- i want a refund || sh
- can i get my money back for the hosting plan || q,e
- please refund my last payment, i didnt use the service || p,m
- i was charged for a renewal i didnt want, refund it || a,m,n
- refund the vps, it never worked properly || a,e
- i want to cancel and get a refund || n
- money back guarantee, i want to use it || i
- how do i request a refund || q
- bought the wrong plan by mistake, need a refund || m,i
- refund for invoice HN-5521 please || e,p
- you charged me twice, refund one || e,a
- i'm not happy with the service, give me my money back || a
- can i get a partial refund for unused months || q,e
- refund the domain i bought yesterday, typo in the name || m,e
- requesting a refund for the ssl i didnt need || n
- refnd please || t,s
- i want my $120 back || e,s
- is the 30 day refund still valid, i signed up 2 weeks ago || q,m
- refund my money for the email plan || e
- i'd like to apply for a refund || p
- refund me now || a,sh
- upgraded by mistake, can i get the difference refunded || m,e
- please process a refund for my account HN-1022 || e,p
- want refund for the unused hosting || s
#none
- qwewqeqw || g
- asdf || g
- ... || g
- ok || sh
- hmm || sh
- ??? || g
- what's the weather tomorrow || o
- write me a poem || o
- how do i get my website to rank higher on google || x
- can you build a website for me || x
- how do i set up a business email || x
- transfer my domain to another registrar || x
- upgrade my hosting plan || x
- reset my cpanel password || x
- do you offer dedicated servers || x
- tell me a joke || o
- who won the oscars this year || o
- lol || s,sh
- pfffff || g
- k || sh
- thanks || sh
- bye || sh
- wxyz || g
- translate thank you to german || o
- mnmnmn || g
"""

B5 = """
@wf synth3_b_05_taskhive_pm
#path greeting
= hi
= hello
= hey
= good morning
= hey there
- hi || sh
- hello || sh
- hey || sh
- good morning || p,sh
- hey there || sh
- hiii || t,sh
- heya || s,sh
- hello taskhive || sh
- morning team || sh
- hi folks || s,sh
- good evening || p,sh
- hi :) || sh
- helloo || t,sh
- hey good afternoon || p
- sup || s,sh
- hi hi || sh
- yo || s,sh
- hey all || sh
- greetings || p,sh
- hi support || sh
- gm || s,sh
- hey! || sh
#path invite_teammate
= invite a teammate
= add a member to my workspace
= send an invite
= add my colleague
= share workspace with someone
- invite my colleague to the workspace || sh
- how do i add a new member to my team || q
- send an invite to alex@studio.io || e
- add 4 people from marketing to our board || e
- my coworker didnt get the invite email, resend it || m,i
- share the workspace with my client || e
- the invite link isnt working for my teammate || i
- can i invite guests who only see one project || q
- add rahul to project apollo || e
- invte teammate || t,sh
- new designer joined, how do i get her in || m,i
- invite 20 users at once from a csv || e
- how many people can i invite on the free plan || q
- add my boss as admin to our workspace || e
- let my freelancer see the tasks || i
- send invites to everyone in my team || sh
- i want to collaborate with my friend on a board || i
- add member pls || s,sh
- invite external partner with view only access || e
- my intern needs to join our workspace || i
- how do i share a project with someone outside the company || q
- add jess@acme.com and tom@acme.com || e
#path remove_user
= remove a user
= kick someone from workspace
= remove a member
= offboard an employee from our team
= revoke someone's access
- remove john from our workspace || e
- how do i kick someone out of the team || q,s
- remove a member who left the company || i
- offboard sarah, she quit last friday || e,m
- revoke access for the contractor || e
- delete a user from my workspace || n
- take mike off project apollo || e
- our intern's internship ended, remove him || m,i
- remove ex-employee ravi@acme.com || e
- kik this guy from the board || t,s
- how do i remove someone from a shared project || q
- remove 3 guests we dont need anymore || e
- my coworker is leaving, deactivate his seat || i
- please remove the freelancer's access, contract ended || p,m
- i accidentally invited the wrong person, remove them || m,n
- remove the old admin from our team || e
- someone i dont know joined our workspace, remove them || a,i
- remove user id U-8812 || e
- unshare the board with my client || i
- free up a seat by removing an inactive user || e
- remove member pls || s,sh
- cut off access for the vendor team || s
#path integration_issue
= slack integration not working
= github sync broken
= google calendar not connecting
= integration error
= zapier not triggering
- slack integration stopped posting updates || e
- github sync is broken, commits not linking || e
- google calendar not connecting to taskhive || e
- zapier zap not triggering on new tasks || e
- integration error when connecting jira || e
- my outlook calendar sync shows old dates || e
- the slack bot isnt responding to commands || e
- cant authorize google drive, keeps failing || e,a
- gitlab webhook returns 401 || e
- teams integration disconnected by itself || e
- intergration not working || t
- api token for integrations expired, how to reconnect || q
- notifications to slack are duplicated || e
- figma embeds not loading in tasks || e
- the dropbox connection keeps asking me to log in again || i
- webhooks stopped firing since yesterday || e
- our salesforce sync isnt updating || e
- tried reconnecting github 3 times, still broken || a,e
- calendar integration shows wrong timezone || e
- zapier says authentication failed with taskhive || e
- slack channel link to project not working || e
- integration broke after your update!! || a
#path export_data
= export my data
= download all tasks as csv
= backup my projects
= export to excel
= get a copy of our data
- export my data || sh
- download all tasks as csv || e
- how do i backup my projects || q
- export board to excel || e
- we need a full export of our workspace before the audit || e
- can i get a copy of all our data || q
- export project apollo with attachments || e
- how to export comments too || q
- download our time tracking report as pdf || e
- exprot to csv || t
- i want a json export of everything || e
- leaving the platform soon, need all my data downloaded first || n
- export completed tasks from last quarter || e
- the export gives me an empty file, how do i get my data out || i
- monthly automated backup possible? || q
- download the gantt chart as image || e
- send me an export of my personal tasks || e
- export all users and their roles || e
- can i export to google sheets || q,e
- i need our data in a spreadsheet for my manager || i
- bulk download all files from projects || e
- archive and download the old workspace || e
#path feature_request
= feature request
= can you add dark mode
= i have a suggestion
= it would be great if
= please build
- can you add dark mode || q
- feature request: recurring tasks every 2 weeks || e
- would be great if we could color code task priorities || i
- please build a home screen widget || p
- i have a suggestion for the calendar view || i
- can you add subtasks inside subtasks || q
- wish there was an offline mode || i
- we'd love a native linear integration || n
- add a way to bulk edit due dates || e
- suggestion: let us pin important comments || e
- fetaure request, time zones per user || t,e
- when will you add gantt charts? || q
- can you make the sidebar collapsible || q
- my team needs a kanban swimlane feature || e
- please add two factor authentication || p
- it would help if exports included comments || n
- idea: templates for weekly sprints || e
- any plans for an ai assistant in tasks? || q
- we need custom fields on tasks, please add || e
- could you support markdown in comments || q
- i'd really like keyboard shortcuts for moving tasks || p
- add emoji reactions to tasks pls || s
#path delete_account
= delete my account
= close my account permanently
= remove my account and data
= erase my profile
- delete my account || sh
- close my account permanently || sh
- i want my account and all my data erased || n
- remove my account and everything in it || i
- how do i delete my taskhive account || q
- please delete my profile, i dont use it anymore || p,m
- gdpr request to delete my personal data || e
- delete account for mike@acme.com, that's me || e
- i want to close my account, not just leave the team || n
- erase my profile || sh
- delte my acount || t
- permanently remove me from taskhive || i
- how long does account deletion take || q
- delete my user account and email me confirmation || e
- im done with this app, delete my account || a,s
- can i delete my account on the mobile app || q
- wipe my account || s,sh
- delete the whole workspace and my account || e
- i signed up by mistake, delete my account || m,i
- remove my login and all my info || i
- deactivate my own account forever || i
- close my account id U-5520 || e
#path thanks
= thanks
= thank you
= bye
= cheers
- thanks || sh
- thank you || sh
- bye || sh
- cheers || s,sh
- thanks a lot || p
- thx || s,sh
- ty || s,sh
- great thanks || sh
- got it thanks || sh
- bye bye || sh
- appreciate it || p
- perfect thank you || p
- thanks for the help || p
- see you || sh
- that's all thanks || i
- tysm || s,sh
- awesome thanks || s
- ok bye || sh
- thank u || s
- many thanks || p
- goodbye || sh
- catch you later || s
#none
- qwewqeqw || g
- asdfgh || g
- ... || g
- hmm || sh
- ok || sh
- ?? || g
- what's the weather in berlin || o
- write me a poem about work || o
- who won the nba finals || o
- what's 2+2 || o
- cancel my subscription || x
- i was charged twice || x
- reset my password || x
- the app keeps crashing || x
- how much is the pro plan || x
- change my email address || x
- tell me a joke || o
- lol || s,sh
- lkjlkj || g
- xcvxcv || g
- brb || s,sh
- can you recommend a laptop || o
- hmm idk || sh
- zzz || g
- movie recommendations please || o
"""

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    write([B1, B2, B3, B4, B5], "saas_it_support", "synth_3_hand_authored",
          os.path.join(root, "data/synthetic/synth_3_b.jsonl"))
