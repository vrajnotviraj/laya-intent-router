"""Synthetic training workflows: airline/travel (synth_2_a) and hotels/rentals (synth_2_b).

Hand-written message pools per intent; each workflow picks intents, a phrasing style,
and ~25 messages per path + ~25 __none__. Run: python training/synth_2.py [--check N]
"""
import json, random, re, sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "synthetic"
FORBIDDEN = ["status or location of their order", "cancel an existing order", "block my card", "what's my balance"]

FILL = {
    "pnr": ["K7Q2ZP", "XJ4R9M", "PL8WQ3", "B2N6TT", "QZ91AF", "HM4KD7", "R8YV2C"],
    "bk": ["#88213", "AB-4471", "#50932", "BK-20931", "#7716", "RES-44120", "HT-9082", "#312765"],
    "flt": ["EK 512", "BA117", "QR 641", "LH 403", "AA2291", "SQ 22", "FZ 1134", "UA 889", "AF 1680"],
    "city": ["Dubai", "London", "Paris", "New York", "Singapore", "Istanbul", "Lisbon", "Toronto", "Bangkok", "Rome", "Sydney", "Cairo"],
    "date": ["12 Oct", "the 18th", "Friday", "3rd November", "Dec 22", "next Monday", "14/11", "Oct 30", "tomorrow"],
    "amt": ["$240", "450 USD", "€180", "£95", "$1,200", "320 dollars", "AED 870", "$64.50"],
    "name": ["John Carter", "Priya Nair", "Maria Lopez", "Ahmed Khan", "Chen Wei", "Sarah O'Neil", "David Kim", "Fatima Ali", "Tom Baker"],
    "phone": ["+1 415 555 0192", "07700 900123", "+44 20 7946 0958", "+971 50 123 4567", "555-0147"],
    "email": ["john.c@gmail.com", "priya.n@outlook.com", "m.lopez@yahoo.com", "dk.travel@proton.me"],
    "company": ["Brightpath Ltd", "Nexa Consulting", "Oakridge Media", "Kestrel Foods Inc"],
    "mem": ["FF 20488312", "7731-0098", "SK44120983", "GM-558210"],
    "tag": ["BA 438812", "EK 772019", "LH 119034", "tag AA 300912"],
    "room": ["214", "1108", "B12", "305", "unit 7", "apt 4C"],
}
FILL["city2"] = FILL["city"]
FILL["date2"] = FILL["date"]


def P(block):
    """'text|tag,tag' lines -> [(text, [tags])]"""
    out = []
    for line in block.strip().splitlines():
        t, _, tags = line.strip().partition("|")
        out.append((t, [x for x in tags.split(",") if x]))
    return out


# ---------------------------------------------------------------- shared generic intents
GREETING = dict(
    desc=["Customer is greeting or starting the conversation", "Hello or hi with no other request"],
    ex=["hi", "hello", "good morning", "hey there", "hi there", "good evening"],
    msgs=P("""
hi|short
hello|short
hey|short
good morning|short
hello there|short
hiii|short,typo
hey there!|short
good evening|short
yo|short,slang
hi team|short
helo|short,typo
morning|short
hi, anyone there?|question
hey, good afternoon|polite
hi hi|short
greetings|short,polite
hey hey|short
hullo|short,typo
gm|short,slang
hello :)|short
hi good morning|short,polite
hey whatsup|short,slang
hello?|short,question
heyyy|short,slang
good afternoon|short,polite
"""))
HUMAN = dict(
    desc=["Customer wants to speak with a live agent or a real person", "Request to be connected to customer support staff"],
    ex=["talk to a human", "agent please", "connect me to customer care", "i want to speak to someone", "real person", "call me back"],
    msgs=P("""
can i talk to a real person|question
agent|short
connect me to customer service please|polite
i don't want a bot, get me a human|angry
speak to someone|short
is there a human i can chat with?|question
call me back on {phone}, i want to speak to staff|entity
human pls|short,slang
transfer me to an agent now|angry
representative|short
this bot is useless. put me through to a person|angry,multi_sentence
can someone from your team call me|question
live chat with agent|short
i'd like to speak to a supervisor please|polite
tlk to human|typo,short
what number do i call to reach an actual person?|question
stop sending me menus, i need a person|angry
need to talk to customer care urgently|angry
operator|short
please escalate this to a human agent|polite
let me chat with support staff|polite
i want a callback from your team|indirect
"""))
THANKS = dict(
    desc=["Customer is saying thanks or ending the conversation", "Thank you or goodbye message closing the chat"],
    ex=["thanks", "thank you", "bye", "that's all", "ok thanks bye", "cheers"],
    msgs=P("""
thanks|short
thank you so much|polite
thx|short,slang
ty|short,slang
bye|short
thanks, that's all|polite
great thanks bye|short
cheers|short,slang
that's everything, thank you|polite
ok thank you|short,polite
appreciate it|short
thanks a lot for the help|polite
bye bye|short
thank u|short,slang
thnks|short,typo
got it, thanks!|short
perfect, thanks|short
goodbye|short
thank you, have a nice day|polite
that solved it, thanks|short
see ya|short,slang
many thanks|short,polite
ok bye|short
tysm|short,slang
all sorted thanks|short
"""))

# ---------------------------------------------------------------- airline & travel
AIR = {
"greeting": GREETING, "talk_to_human": HUMAN, "thanks_goodbye": THANKS,
"flight_status": dict(
    desc=["Customer wants to know if their flight is on time, delayed, or which gate it leaves from", "Passenger asking for the live status, departure time or arrival time of a flight"],
    ex=["is my flight on time", "flight status", "has EK 512 been delayed", "what gate does my flight leave from", "has the flight landed", "departure time for my flight today", "check flight status"],
    msgs=P("""
is {flt} on time today?|question,entity
flight status {flt}|entity,short
what time does my flight to {city} actually leave, the app shows two different times|multi_sentence,entity
hi, my sister is flying in on {flt} tonight. has it landed yet?|multi_sentence,entity,question
which gate is {flt} boarding from|entity
is the 6am flight to {city} running late|entity
has my flight been pushed back? booking {pnr}|entity,question
im at the airport and the board says nothing about my flight, is it still going|multi_sentence,indirect
flght {flt} delayd??|typo,entity
any update on departure for {flt}|entity
is the flight leaving on time or not, ive been waiting 2 hrs with zero info|angry,multi_sentence
could you please tell me the current status of flight {flt}?|polite,entity,question
when is {flt} expected to land in {city}|entity,question
my dad is picking me up, what time will we actually arrive|indirect
did they change the gate for my flight|question
wats the eta on {flt}|slang,typo,entity
is my flight still on schedule for tomorrow morning|question
board just says delayed with no time. how long??|angry,indirect,multi_sentence
has the {city} flight taken off yet|question,entity
status pls|short,slang
departure gate for {pnr}|entity,short
we are on {flt} {date}, is it running on time?|entity,question
""")),
"book_flight": dict(
    desc=["Customer wants to book a new flight ticket", "User is looking to buy a ticket or search for available flights"],
    ex=["book a flight", "i want to buy a ticket", "flights to dubai next week", "search flights", "need a one way ticket", "book tickets for 2 adults"],
    msgs=P("""
i want to book a flight to {city} on {date}|entity
need 2 tickets to {city} next friday, cheapest possible|entity
do you have any flights from {city} to {city2} this weekend|entity,question
book me a one way ticket pls|slang
looking for a return flight for 3 people, 2 adults 1 child, leaving {date}|entity
how do i buy a ticket on whatsapp|question
hi! planning a trip to {city} in december, can you show me flights?|polite,multi_sentence,entity
wanna fly to {city} tmrw morning whats available|slang,entity
i'd like to book the evening flight to {city} please|polite,entity
cheapest fare to {city} in march?|entity,question
bok a flite to {city}|typo,entity
need to get to {city} urgently for a funeral. earliest flight you have?|multi_sentence,entity
can i book a ticket for my mom from here|question
new booking please|short,polite
are there direct flights to {city}|question,entity
what's the price for business class to {city} on {date}|entity,question
i want to buy tickets for our family holiday, 4 people|entity
flights available {city} to {city2} {date}?|entity
ticket to {city}|short,entity
my company needs to fly 5 staff to {city} next month. can we book here?|multi_sentence,question,entity
hey can u find me a flight under {amt}|slang,entity
book flight|short
""")),
"change_flight": dict(
    desc=["Customer wants to change the date, time or route of an existing flight booking", "Passenger wants to reschedule their flight"],
    ex=["change my flight date", "reschedule my booking", "move my flight to tomorrow", "can i fly a day earlier", "switch to a later flight"],
    msgs=P("""
i need to change my flight to {date}, booking {pnr}|entity
can i move my flight to the next day?|question
reschedule {pnr} to the evening flight please|entity,polite
my meeting got moved so i need to fly out a day earlier|indirect,multi_sentence
is it possible to switch to a later flight on the same day|question
chnage date of my tkt|typo,slang,short
how much does it cost to change the date on my ticket|question
i booked {city} but i actually want to go to {city2} instead, can we swap it|multi_sentence,entity
pls push my return flight by one week|slang
hi, i'm on {flt} on {date} but i can't make it. can i take the one on the 28th instead?|multi_sentence,entity
want to change travel date|short
can i bring my flight forward to this friday|question
I would like to amend the departure time on booking {bk}|polite,entity
need an earlier flight home, my kid is sick|multi_sentence,indirect
i asked yesterday and nothing happened. i STILL need my date moved to {date}|angry,entity,multi_sentence
change {pnr} to {date}|entity,short
is there a way to change the return leg only?|question
can you put me on tomorrow's flight instead of today's|question
moving my trip, need new dates|short,slang
date change for passenger {name}, ref {pnr}|entity
my visa appointment got delayed so i need to postpone the flight by 2 weeks|indirect,multi_sentence
""")),
"cancel_booking": dict(
    desc=["Customer wants to cancel their flight booking", "Passenger no longer wants to travel and asks to cancel the ticket"],
    ex=["cancel my flight", "i want to cancel my ticket", "cancel booking", "i'm not travelling anymore", "please cancel my reservation"],
    msgs=P("""
please cancel my booking {pnr}|polite,entity
i want to cancel my flight on {date}|entity
not travelling anymore, cancel it|slang,indirect
cancel {pnr}|short,entity
how do i cancel my ticket|question
hi, my trip got called off so i need to cancel both tickets under {name}|multi_sentence,entity
cancle my flite|typo,short
can i cancel just one passenger from the booking?|question
i booked by mistake. please cancel it now|multi_sentence
we won't be flying to {city} anymore, kindly cancel the reservation|polite,indirect,entity
cancel my return flight only, keep the outbound|multi_sentence
I've been trying to cancel for 3 days on your app and it keeps failing. cancel it!!|angry,multi_sentence
is it too late to cancel a flight that leaves tomorrow|question
cancel booking ref {bk} please|entity,polite
i dont want this ticket anymore|indirect
my father passed away and we can't travel, need to cancel {pnr}|multi_sentence,entity
pls cxl my booking|slang,short
want to cancel the {city} trip|entity
cancel the whole thing, all 4 passengers|multi_sentence
can you cancel my {date} flight|entity,question
""")),
"refund_status": dict(
    desc=["Customer is asking about a refund they are still waiting for", "Passenger wants to know when the money for a cancelled ticket will come back"],
    ex=["where is my refund", "refund status", "i haven't received my refund", "when will i get my money back", "refund not credited"],
    msgs=P("""
where is my refund for {pnr}? cancelled 2 weeks ago|entity,multi_sentence,question
refund status {bk}|short,entity
still no money back in my account|indirect
you said 7 days for the refund, it's been 20. where is my {amt}|angry,entity,multi_sentence
when will i get my money back for the cancelled flight|question
refnd not recieved yet|typo
hi, the airline cancelled my flight and i was promised a refund. any update?|multi_sentence,question
has my refund been processed?|question
i got a refund but it's only half the amount, why|multi_sentence,question
can you check on the refund for {name}, booking {pnr}|entity,polite
my card still hasn't been credited for the ticket i cancelled|indirect
how long do refunds take to show up|question
refund??|short
its been a month and no refund. this is theft|angry,multi_sentence
could you kindly share the refund reference number for {bk}?|polite,entity,question
cancelled my ticket on {date}, money not back yet|entity,multi_sentence
is my refund coming to my card or as a voucher|question
wheres my money|slang,short,angry
the refund shows processed but my bank has nothing|multi_sentence,indirect
checking on my refund of {amt}|entity
""")),
"baggage_allowance": dict(
    desc=["Customer is asking how much luggage they can bring or about bag weight and size limits", "Question about cabin and checked baggage allowance or buying extra baggage"],
    ex=["how many bags can i take", "baggage allowance", "what is the weight limit for luggage", "can i add an extra bag", "cabin bag size", "buy extra kilos"],
    msgs=P("""
how many kg can i check in on economy|question
baggage allowance for {pnr}?|entity,short
can i bring 2 carry ons|question
what size can my cabin bag be|question
i need to add an extra 10kg to my booking|entity
is a guitar allowed as hand luggage|question
hi, flying to {city} with a baby. do strollers count as a bag?|multi_sentence,question,entity
whats the weight limit on international flights|question
can i carry my golf bag|question
bagage alownce|typo,short
how much to buy extra luggage|question
is 25kg ok or will i get charged|question
my ticket says 0PC, does that mean no checked bag?|question,indirect
i'm bringing a laptop and a backpack. is that okay for cabin?|multi_sentence,question
can my wife and i pool our baggage allowance|question
luggage limit?|short
how many suitcases for business class|question
i want to pre purchase baggage for my flight on {date}|entity
could you please confirm the cabin baggage dimensions?|polite,question
do liquids have a limit in hand baggage|question
""")),
"lost_baggage": dict(
    desc=["Customer's checked bag is lost, delayed or damaged after the flight", "Passenger wants to report or track missing luggage"],
    ex=["my bag didn't arrive", "lost luggage", "my suitcase is damaged", "track my missing bag", "baggage not on the belt"],
    msgs=P("""
my bag didnt come out at {city} airport|entity
lost luggage on {flt}|entity,short
waited at the belt for an hour, no suitcase. what now|multi_sentence,angry
i filed a report {bk}, any news on my bag?|entity,question
my suitcase arrived with a broken wheel|indirect
where is my luggage, its been 3 days|angry,multi_sentence
lost bagage report|typo,short
hi, i landed this morning from {city} and one of my 2 bags is missing|multi_sentence,entity
my bag was opened and things are missing from it|indirect
how do i report a damaged bag|question
can you deliver my delayed bag to my hotel|question
the tag number is {tag}, please trace it|entity,polite
my luggage went to the wrong city apparently|indirect
bag missing|short
i have no clothes, my bag never showed up, i need this sorted today|angry,multi_sentence
could you please give me an update on my delayed baggage?|polite,question
stroller was not returned at the gate after landing|indirect
my suitcase got soaked and ruined on the flight|indirect
bag lost on connection in {city}|entity
reporting missing luggage for {name}|entity
""")),
"web_checkin": dict(
    desc=["Customer wants to check in online or get their boarding pass", "Passenger needs help with web check-in or downloading a boarding pass"],
    ex=["online check in", "send my boarding pass", "how do i check in", "web check-in not working", "i need my boarding pass"],
    msgs=P("""
how do i check in online for {pnr}|entity,question
send me my boarding pass pls|slang
web checkin is not working on the app|indirect
when does online check in open|question
i can't download my boarding pass, it just shows an error|multi_sentence
check in for {flt} {date}|entity,short
boarding pass|short
can i check in on whatsapp|question
chek in onlin|typo,short
it says check-in unavailable for my booking, why|question,indirect
can you resend the boarding pass to {email}|entity
hi, travelling with my 2 kids. how do i check all 3 of us in online?|multi_sentence,question
i checked in but didn't get the pass on email|multi_sentence,indirect
is mobile boarding pass accepted or do i need a printout|question
i need to check in now, flight in 4 hrs|multi_sentence
please help me complete web check in for {name}|polite,entity
trying to check in for an hour, site keeps crashing. useless|angry,multi_sentence
get boarding pass {pnr}|entity,short
do i have to check in at the airport or can i do it here|question
where can i find my boarding pass after check in|question
""")),
"seat_selection": dict(
    desc=["Customer wants to choose or change their seat on the flight", "Passenger asking for a window or aisle seat, extra legroom, or to sit together"],
    ex=["choose my seat", "i want a window seat", "change my seat", "can we sit together", "extra legroom seat"],
    msgs=P("""
can i get a window seat on {flt}|entity,question
i want to change my seat to an aisle|polite
we're 3 people, can you seat us together|multi_sentence,question
how much is an exit row seat|question
select seat for {pnr}|entity,short
my seat is 42E, middle, i want something better|entity,indirect
seat change pls|short,slang
is there any extra legroom seat available on the {date} flight|entity,question
they split me and my wife in different rows, fix it|angry,indirect
can i pick seats for free or is it paid|question
wndow seat plz|typo,slang,short
my kid is 5 and seated away from me. that's not acceptable|angry,indirect,multi_sentence
i'd like to pre-book seat 12A please|polite,entity
is 23C an aisle?|entity,question
hi! could you assign me a seat near the front? i get airsick|polite,multi_sentence
change seat for {name}|entity,short
i paid for a seat but the app shows none assigned|indirect,multi_sentence
want to sit next to my friend who booked separately, ref {bk}|entity
move me to a front row seat|short
are there any empty rows so i can stretch out|question,indirect
""")),
"special_assistance": dict(
    desc=["Customer needs wheelchair, medical or special travel assistance", "Passenger requesting help for elderly, disabled, pregnant or unaccompanied minor travellers"],
    ex=["i need a wheelchair", "assistance for my elderly mother", "flying while pregnant", "unaccompanied minor service", "help at the airport for disabled passenger"],
    msgs=P("""
i need a wheelchair at the airport for {pnr}|entity
my mother is 82 and can't walk long distances. can someone help her to the gate?|multi_sentence,indirect
wheelchair assistance on arrival in {city} please|entity,polite
is it ok to fly at 30 weeks pregnant|question
my 12 year old is flying alone, what service do you have|multi_sentence,question
need help boarding, i just had knee surgery|indirect,multi_sentence
weelchair request|typo,short
can i bring my oxygen concentrator on board|question
my husband uses a wheelchair, what do we need to do before flying|multi_sentence,question
special assistance for {name}|entity,short
hi, my grandfather has dementia. can staff escort him through transit in {city}?|multi_sentence,question,entity
do you provide help for deaf passengers|question
please arrange assistance, my son is autistic and gets overwhelmed at security|polite,multi_sentence
requested a wheelchair last time and nobody came. make sure it's there this time|angry,multi_sentence
meet and assist service for elderly parent|short
i have a heart condition, do i need a medical form to fly|question
can someone push my wheelchair to the connecting flight|question
booking an escort for my unaccompanied minor|indirect
need a buggy at the airport, can't walk far|slang,indirect
""")),
"loyalty_points": dict(
    desc=["Customer is asking about frequent flyer miles or loyalty points", "Member wants to check missing miles, tier status or redeem points"],
    ex=["how many miles do i have", "my points are missing", "redeem miles for a ticket", "join frequent flyer", "tier status", "miles not credited"],
    msgs=P("""
how many miles do i have, member no {mem}|entity,question
my miles from last trip didn't get added|indirect
can i use points to pay for a flight|question
how do i join your frequent flyer program|question
missing points for {flt} on {date}|entity
when do my miles expire|question
how many points to upgrade to business|question
i'm gold member but the app still shows silver|indirect,multi_sentence
milage not credited|typo,short
can i transfer my points to my husband|question
hi, i flew 4 times this year and have zero points showing. what's going on|multi_sentence,angry
miles total?|short
redeem miles|short
please add my membership number {mem} to booking {pnr}|polite,entity
do i earn miles on partner airlines|question
i lost 20000 miles, they just vanished!!|angry,entity
how to reach platinum tier|question
my loyalty card number is {mem}, can you check my miles|entity
can i buy extra miles|question
forgot my frequent flyer number|indirect
""")),
"delay_compensation": dict(
    desc=["Customer wants compensation, vouchers or meals because their flight was delayed or they were denied boarding", "Passenger asks what they are entitled to after a long delay or overbooking"],
    ex=["compensation for delay", "my flight was 5 hours late, what do i get", "meal voucher", "i was denied boarding", "hotel for delayed flight"],
    msgs=P("""
my flight was delayed 6 hours, i want compensation|multi_sentence
do i get anything for the 4 hour delay on {flt}|entity,question
we were bumped off an overbooked flight, what are we entitled to|multi_sentence,question
meal voucher for delay?|short
compensation for {pnr}, delayed overnight|entity
stuck at the airport all night because of your delay. who pays for my hotel|angry,multi_sentence
compensaton delay|typo,short
hi, {flt} on {date} arrived 5 hrs late and i missed my meeting. is there compensation?|multi_sentence,entity,question
how do i apply for delay compensation|question
denied boarding at the gate today even with a ticket. i want money for this|angry,multi_sentence
the delay ruined day one of our holiday, we expect something back|indirect,angry
entitled to EU261?|short,entity
please let me know what compensation applies for a 3 hour delay|polite
our connection was missed due to your delay, can we get vouchers|multi_sentence,question
is there a voucher for waiting 7 hours|question
you delayed us twice this month, i want compensation|angry
compensation request for {name}|entity,short
we sat on the plane for 4 hrs before takeoff, anything for that?|multi_sentence,question
can i get lounge access since my flight is delayed|question
i applied for delay compensation last month and got no reply|multi_sentence,indirect
""")),
"travel_docs": dict(
    desc=["Customer is asking about passport, visa or ID requirements for travel", "Question about which documents are needed to fly"],
    ex=["do i need a visa", "passport requirements", "what documents do i need", "can i fly with an expired id", "transit visa"],
    msgs=P("""
do i need a visa for {city}|entity,question
what documents do i need to fly with my baby|question
my passport expires in 4 months. can i still travel?|multi_sentence,question
transit visa needed for a layover in {city}?|entity,question
can i fly domestic with just my driving licence|question
visa requirments for indian passport to {city}|typo,entity
does my kid need their own passport|question
hi, travelling on a green card. is that enough to board to {city}?|multi_sentence,entity,question
what id do i show at the gate|question
docs needed?|short
is a covid certificate still needed for {city}|entity,question
please confirm what travel documents are required for {city}|polite,entity
do i need to print my e-visa|question
can i travel with a photocopy of my passport|question
passport lost, can i still take my flight tomorrow|multi_sentence,question
what do minors need to travel with one parent|question
do u need a visa for a 2 hr stopover|slang,question
ETA required for UK?|short,entity
got turned away at check in last time over documents. what exactly do i need for {city}?|angry,multi_sentence,entity
""")),
"pet_travel": dict(
    desc=["Customer wants to fly with a pet", "Question about taking a dog, cat or other animal on the flight"],
    ex=["can i bring my dog", "pet in cabin", "travel with my cat", "pet carrier size", "fly with my pet"],
    msgs=P("""
can my dog fly in the cabin with me|question
how much to bring a cat on board|question
what size carrier do i need for my pet|question
i want to travel with my puppy to {city}|entity
pets allowed?|short
can i take my 2 cats on {flt}|entity,question
hi, relocating to {city} with our golden retriever. how does cargo work for pets?|multi_sentence,entity,question
do you allow rabbits|question
pet travel rules for international|short
my dog is 9kg, is that ok for cabin|question,entity
add a pet to booking {pnr}|entity
can i bring my parrot|question
dog in cabn|typo,short
last time your staff were rude about my cat carrier. what are the actual rules|angry,multi_sentence
please add my small dog to my reservation for {date}|polite,entity
does my pet need a health certificate to fly|question
is there a fee for pets in the hold|question
flying with a hamster possible?|question
we have a french bulldog, can it fly|question,indirect
""")),
"invoice": dict(
    desc=["Customer needs an invoice or receipt for their ticket", "User asking for a tax invoice or payment receipt for a booking"],
    ex=["send invoice", "i need a receipt", "tax invoice for my booking", "invoice in company name", "download receipt"],
    msgs=P("""
can you send me the invoice for {pnr}|entity,question
i need a receipt for my company expenses|indirect
invoice pls|short,slang
please issue the invoice in my company name, {company}|polite,entity
where can i download the receipt for my ticket|question
recipt for booking {bk}|typo,entity
the invoice has the wrong address, can you reissue it|multi_sentence,question
my finance team needs a tax invoice for the {date} trip|entity
didnt get any email receipt after paying {amt}|entity,indirect
need a VAT invoice|short
hi, i paid for 3 tickets. can i get one invoice for all of them?|multi_sentence,question
invoice for the baggage fee i paid at the airport|entity
asked for the invoice 3 times already, still nothing|angry,multi_sentence
can i have separate receipts per passenger|question
send receipt to {email}|entity,short
accounts department is asking for proof of payment for the flight|indirect
how do i get a bill for my seat upgrade|question
could you email me an itemized receipt?|polite,question
billing document for {name}|entity,short
need an invoice with our company tax number|entity
""")),
}
AIR_EXTRA_MISSING = P("""
my name is misspelled on the ticket, can you correct it|missing_intent
is there wifi on board|missing_intent,question
what meals do you serve on the flight to {city}|missing_intent,entity
can i buy a gift card for my brother|missing_intent
do you offer holiday packages with hotel included|missing_intent,question
is there a lounge i can use at {city} airport|missing_intent,entity
how do i become a cabin crew with you|missing_intent,question
can i order a vegetarian meal for {pnr}|missing_intent,entity
where do i leave feedback about the crew|missing_intent
can i bring my own food through security|missing_intent,question
""")
AIR_CONFLICTS = [("change_flight", "book_flight"), ("web_checkin", "seat_selection"), ("travel_docs", "pet_travel")]

# ---------------------------------------------------------------- hotels & rentals
HOTEL = {
"greeting": GREETING, "talk_to_human": HUMAN, "thanks_goodbye": THANKS,
"new_booking": dict(
    desc=["Customer wants to book a room or a stay", "Guest asking about availability and prices to make a new reservation"],
    ex=["book a room", "availability for this weekend", "need a room for 2 nights", "do you have rooms free", "reserve a stay", "price per night"],
    msgs=P("""
do you have a double room free for {date}|entity,question
i want to book 2 nights from friday|entity
need a room for 4 adults this weekend|entity
is the sea view suite available next week|question
booking for 3 nights, {date}, 2 guests|entity
hi! we're coming to {city} for a wedding. can we book 5 rooms?|multi_sentence,entity,question
how much per night for a king room|question
any availability tonight? just landed|multi_sentence,question
bok a room|typo,short
want to reserve the whole villa for new year|entity
can i book the apartment for a month|question
looking for a place for 2 with a kitchen, {date} to {date2}|entity
please book me a single room with breakfast|polite
room for tonight?|short
what's your best rate for a 7 night stay|question
we need a family room, 2 kids, from the 12th|entity
i'd like to make a reservation for my parents|polite
do u have rooms free in december|slang,question
book the studio for {name}, arriving {date}|entity
tried booking on your site 3 times and it fails. just book it for me here|angry,multi_sentence
price for a room {date}?|entity,short
new reservation|short
""")),
"modify_reservation": dict(
    desc=["Customer wants to change the dates, guests or room type of an existing reservation", "Guest wants to extend, shorten or update their booking"],
    ex=["change my booking dates", "add one more night", "change room type", "modify reservation", "add a guest to my booking", "extend my stay"],
    msgs=P("""
can i extend my stay by one more night|question
change my check-in date to {date}, booking {bk}|entity
i need to switch from a twin to a double room|entity
add one more guest to reservation {bk}|entity
we're arriving a day later, can you move the booking|multi_sentence,question
modify booking {bk}|entity,short
shorten my stay to 2 nights instead of 4|entity
chnge my dates pls|typo,slang,short
hi, our flight got moved so we need the room from the 14th not the 13th|multi_sentence,entity,indirect
can i upgrade my room to a suite for the same dates|question
please update the guest name on the booking to {name}|polite,entity
we'll stay till sunday now, not saturday|indirect
change reservation {bk} to 3 adults|entity
i asked to change my dates yesterday and nothing happened|angry,multi_sentence
move my booking to next month|indirect
can i swap my room for one with a balcony, same booking|question
extend booking|short
i booked one bed, need two beds instead|indirect
could you push my reservation back by one week?|polite,question
""")),
"cancel_reservation": dict(
    desc=["Customer wants to cancel a hotel or rental reservation", "Guest is no longer coming and asks to cancel the booking"],
    ex=["cancel my booking", "cancel reservation", "we're not coming anymore", "please cancel my stay", "cancel the apartment"],
    msgs=P("""
please cancel reservation {bk}|polite,entity
i need to cancel my stay for {date}|entity
we're not coming anymore, cancel it|indirect
cancel booking|short
how do i cancel my reservation|question
cancle my room|typo,short
hi, trip is off due to a family emergency. please cancel both rooms under {name}|multi_sentence,entity,polite
can i cancel just one of the two rooms|question
cancel the apartment booking for next week|entity
booked the wrong hotel by accident, cancel it please|multi_sentence
i want to cancel, confirmation number {bk}|entity
is free cancellation still possible for my booking|question
cancel everything, we found another place|multi_sentence,indirect
i've emailed 3 times to cancel. CANCEL IT|angry,multi_sentence
our plans changed, we won't need the villa|indirect
cxl my res {bk}|slang,entity,short
can you cancel my stay tonight, i'm stuck in another city|multi_sentence,question
please cancel the reservation for {name} on {date}|polite,entity
i don't need the room anymore|indirect
cancel {bk}|short,entity
""")),
"refund_status": dict(
    desc=["Customer is asking about the status of a refund", "Guest wants to know when money for a cancelled or overcharged stay will come back"],
    ex=["where is my refund", "refund status", "money not received back", "when will i get my refund", "refund still pending"],
    msgs=P("""
where is my refund for {bk}|entity,question
cancelled my stay 10 days ago, still no refund|multi_sentence,entity
refund status pls|short,slang
when will the {amt} come back to my card|entity,question
you promised a refund for the broken ac room, where is it|angry,multi_sentence
refund not recieved|typo,short
hi, just checking whether my refund has been processed?|polite,question
how long does a refund take|question
the refund was less than i paid, why|multi_sentence,question
my bank says nothing came in from you yet for the refund|indirect
booking {bk} was cancelled by the host, waiting on my money back|entity,multi_sentence
refund??|short
its been 6 weeks, i want my refund now|angry,multi_sentence
can you share the refund transaction id|question
did the refund go to my card or wallet|question
money back for the cancelled apartment?|indirect,short
please check the refund for {name}|polite,entity
still waiting on refund|short
your email said refund issued on {date} but nothing yet|entity,multi_sentence
any update on my refund of {amt}|entity
""")),
"security_deposit": dict(
    desc=["Guest is asking about the security deposit: the amount, the card hold, or when it is released", "Question about the damage deposit for a rental"],
    ex=["security deposit", "when do i get my deposit back", "how much is the deposit", "deposit still on hold", "damage deposit"],
    msgs=P("""
how much is the security deposit for the apartment|question
when will my deposit be released, checked out {date}|entity,multi_sentence
deposit still blocked on my card|indirect
why was {amt} deducted from my damage deposit|entity,question,angry
do i pay the deposit in cash or card|question
secuirty deposit?|typo,short
hi, we left the place spotless. when is the deposit returned?|multi_sentence,question
is the deposit refundable|question
the host is keeping my deposit for no reason|angry,indirect
deposit hold for booking {bk}|entity,short
can i skip the damage deposit|question
how long do you hold the deposit after checkout|question
there's a {amt} pre-authorization on my card from the rental deposit, when does it drop|entity,question
please release my deposit|polite
nobody explained the deposit when i booked|indirect,angry
deposit amount for villa|short
got my deposit back minus $50, what for|multi_sentence,question,entity
is the deposit taken at check-in or at booking|question
can the deposit be paid by bank transfer|question
still waiting on my deposit from last week|multi_sentence
""")),
"checkin_checkout_times": dict(
    desc=["Guest is asking what time check-in or check-out is", "Question about standard arrival and departure times"],
    ex=["what time is check in", "check out time", "when can i arrive", "check in hours", "by when do we leave the room"],
    msgs=P("""
what time is check in|question
check-out time?|short
when can we arrive tomorrow|question
what's the standard checkout time|question
from what time can i get the keys|question
chek in time|typo,short
hi, arriving on {date}. what time does check-in start?|multi_sentence,entity,question
by when do we have to leave the room on sunday|question
is checkin at 2 or 3pm|question
checkout hours?|short
do you have 24 hour check in|question
what time does reception close for check-in|question
when does the apartment become available on arrival day|question,indirect
could you tell me the check in and check out times please|polite,question
need to know checkout time for booking {bk}|entity
arriving at midnight, is check in still open|multi_sentence,question
last time we waited 2 hours for the room at 3pm. what is the actual check in time?|angry,multi_sentence,question
what hour is check out|question
check in from?|short
wat time do we need to be out by|typo,question
""")),
"early_late_request": dict(
    desc=["Guest requests an early check-in or a late check-out", "Guest wants to arrive before or leave after the standard times"],
    ex=["can i check in early", "late checkout please", "arrive at 8am", "stay in the room until 4pm", "early check-in request"],
    msgs=P("""
can i check in early, around 9am|question,entity
late checkout please, till 2pm|polite,entity
our flight lands at 6am, is early check in possible|multi_sentence,question
can we keep the room until 5pm on sunday|question,entity
request early check-in for booking {bk}|entity
late chekout?|typo,short
flight is at 10pm, any chance of staying in the room longer?|multi_sentence,question,indirect
how much for a late check out|question
hi, we arrive before noon. can the apartment be ready early?|multi_sentence,question
early check in|short
please give us late checkout, it's our anniversary|polite,multi_sentence
can i get the keys at 10 instead of 3|question
i'm a gold member, i want 4pm checkout|entity
can we check out at 1 instead|question
is it possible to check in at 7am? i'll pay extra|question,multi_sentence
we need the room early, the baby needs to sleep|indirect,multi_sentence
extend checkout by 2 hrs pls|slang
you denied my late checkout last time, i really need it this time|angry,multi_sentence
early arrival request for {name}|entity,short
""")),
"amenities": dict(
    desc=["Guest is asking about facilities like wifi, pool, gym, breakfast or spa", "Question about what the property offers and its facility hours"],
    ex=["is there wifi", "do you have a pool", "breakfast timing", "gym hours", "is breakfast included", "what facilities do you have"],
    msgs=P("""
is there a pool|question
what's the wifi password|question
breakfast timings?|short
do you have a gym|question
is breakfast included in my booking {bk}|entity,question
does the apartment have a washing machine|question
is the spa open on sundays|question
do rooms have a kettle|question
any kids club or play area|question
wat time does the pool close|typo,question
hi, does the villa have a bbq grill we can use?|multi_sentence,question
is there air conditioning in the bedrooms|question
is there a hairdryer in the room|question
what facilities do you have|question
is the pool heated in winter|question
does the gym have free weights|question
is there a dishwasher in the kitchen|question
coffee machine in the unit?|short,question
till what time is the restaurant open|question
do you have a sauna|question
""")),
"parking": dict(
    desc=["Guest is asking about parking availability or cost", "Question about where to park a car at the property"],
    ex=["is there parking", "parking cost", "can i park my car", "valet parking", "where do i park"],
    msgs=P("""
is there parking at the hotel|question
how much is parking per day|question
can i park my car overnight|question
do you have valet|question,short
where do i park when i arrive|question
parkng available?|typo,short
hi, we're driving in with a van. is there space for it?|multi_sentence,question,indirect
is street parking safe around the apartment|question
do i need to reserve a parking spot|question
parking for 2 cars {date}|entity
is there an ev charger in the car park|question
free parking?|short
the parking gate won't open, i'm stuck outside|angry,indirect,multi_sentence
can i leave my car there after checkout|question
height limit for the garage?|question
please reserve a parking space for booking {bk}|polite,entity
where's the nearest public car park|question
motorbike parking?|short
do you charge for parking? it wasn't mentioned when i booked|multi_sentence,question
""")),
"room_issue": dict(
    desc=["Guest reports a problem in the room such as broken AC, no hot water, noise or a dirty room", "Complaint about something broken or wrong in the accommodation"],
    ex=["ac not working", "no hot water", "room is dirty", "toilet is blocked", "too noisy", "something is broken in my room"],
    msgs=P("""
the ac in room {room} isnt working|entity
no hot water in the shower|indirect
the room is filthy, hair everywhere|angry
toilet is blocked|short
there's loud music next door, cant sleep|multi_sentence,indirect
tv doesnt turn on|slang
bed has stains on the sheets, disgusting|angry
hi, the heater in the apartment is broken and it's freezing|multi_sentence
there's water dripping from the ceiling|indirect
ac not wrking room {room}|typo,entity
smell of smoke in our non smoking room|indirect
cockroach in the bathroom!!|angry
please send someone, the sink is overflowing|polite,multi_sentence
the fridge is not cooling|indirect
power went out in our unit|indirect
the bathroom door lock is jammed|indirect
room smells of damp|indirect
window won't close and it's so cold|multi_sentence
the shower drain is clogged, water everywhere|multi_sentence
lights keep flickering in {room}|entity
""")),
"housekeeping_request": dict(
    desc=["Guest requests extra towels, cleaning, toiletries or other items for the room", "Request for housekeeping service"],
    ex=["extra towels please", "clean my room", "more pillows", "send toiletries", "change the bedsheets"],
    msgs=P("""
can i get extra towels|question
please clean our room today|polite
2 more pillows to room {room}|entity
we need more toilet paper|indirect
can someone make up the room around noon|question
send shampoo and soap pls|slang
xtra blanket plz|typo,slang,short
hi, could we get a baby cot in the room?|polite,question,multi_sentence
change the bedsheets please|polite
can housekeeping skip our room today|question
need fresh towels in {room}|entity
more coffee pods for the apartment|indirect
can we get an iron and ironing board|question
please take out the trash|polite
nobody has cleaned our room for 2 days. please send someone|angry,multi_sentence
dental kit?|short
mid stay cleaning for the villa|short
extra bed for our son|indirect
could i have a bathrobe sent up|polite,question
towels|short
""")),
"lost_item": dict(
    desc=["Guest left something behind or lost an item during their stay", "Lost and found enquiry"],
    ex=["i left my charger in the room", "lost and found", "forgot my jacket", "did you find my watch", "left something behind"],
    msgs=P("""
i left my phone charger in room {room}|entity
did your staff find a black jacket in our room|question
forgot my passport in the room safe!!|angry
lost and found|short
i think i left my glasses at the pool yesterday|indirect
checked out this morning, my laptop is still in the apartment|multi_sentence,indirect
can you post my forgotten earrings to my home address|question
left somthing in the room|typo
hi, my daughter's teddy bear got left behind. it's really important to her|multi_sentence,polite
was a gold watch handed in? booking {bk}|entity,question
i lost my wallet somewhere in the hotel|indirect
forgot my shoes under the bed|indirect
my kindle is missing, please check room {room}|entity,polite
i called twice about my left bag and nobody got back to me|angry,multi_sentence
did anyone find a ring in the bathroom|question
i left a charger behind|short
can i collect my forgotten items tomorrow|question
is my umbrella there? left it in the lobby|multi_sentence
we left the kids' ipad in the villa|indirect
left my medication in the fridge of the unit|indirect
""")),
"invoice": dict(
    desc=["Guest needs an invoice or receipt for their stay", "Request for a bill, folio or tax invoice"],
    ex=["send invoice", "i need a receipt", "invoice for my stay", "invoice in company name", "final bill"],
    msgs=P("""
can i get the invoice for my stay|question
i need a receipt for booking {bk}|entity
please send the bill to {email}|polite,entity
invoice in company name {company} please|entity,polite
folio for room {room}|entity,short
recipt pls|typo,slang,short
hi, my employer needs an itemized invoice for last week's stay|multi_sentence
the invoice shows the wrong dates, can you fix it|multi_sentence,question
vat invoice needed|short
didn't get any receipt after checkout|indirect
can you split the bill into 2 invoices|question
where do i download my invoice|question
i've been asking for the invoice for a week|angry,multi_sentence
need proof of payment for my stay for my visa application|indirect
send me the final bill|polite
could you please resend the invoice for {name}?|polite,entity,question
billing statement for my 2 week stay|entity
invoice|short
accounts need a copy of the receipt for {amt}|entity,indirect
invoice with our tax number on it please|polite
""")),
"pet_policy": dict(
    desc=["Guest is asking whether pets are allowed at the property", "Question about the pet policy or pet fees"],
    ex=["are pets allowed", "can i bring my dog", "pet friendly", "pet fee", "dogs allowed?"],
    msgs=P("""
are dogs allowed|question
can i bring my cat|question
is the apartment pet friendly|question
pet fee?|short
we have a small dog, can he stay with us|multi_sentence,question
pets alowed?|typo,short
hi, travelling with 2 labradors. any rooms that allow big dogs?|multi_sentence,question
is there a charge for bringing a pet|question
can my dog be left alone in the room|question
do you allow cats in the villa|question
bringing my puppy, is that ok|indirect,question
pet policy|short
please confirm my dog is allowed for booking {bk}|polite,entity
are there dog bowls or beds provided|question
any weight limit for pets|question
last hotel turned us away with our dog, i need to be sure before booking|multi_sentence,angry
can i bring my bird in its cage|question
do you accept service dogs|question
hamster allowed?|short
""")),
"directions_location": dict(
    desc=["Guest is asking for the address, directions or how to get to the property", "Question about the location of the hotel or rental"],
    ex=["what's the address", "how do i get there from the airport", "send location", "nearest metro", "where are you located"],
    msgs=P("""
what's the hotel address|question
send me the location pin|short
how do i get there from the airport|question
is it walking distance from the train station|question
hi, the taxi driver can't find you. where exactly are you?|multi_sentence,question,angry
directions pls|short,slang
adress of the apartment?|typo,short
how far is it from {city} centre|entity,question
nearest metro stop to the hotel|short
we're lost, google maps takes us to a dead end|multi_sentence,indirect
can you share the google maps link|question
how long by taxi from the airport|question
please tell me the exact address for booking {bk}|polite,entity
which street is the building on|question
is the property near the beach|question
what's the landmark near your place|question
how do i reach you by bus|question
location?|short
""")),
"access_instructions": dict(
    desc=["Guest needs the door code, keys or self check-in instructions for the rental", "Question about how to get into the property on arrival"],
    ex=["door code", "how do i get the keys", "self check in instructions", "key box code", "lockbox not opening", "entry code"],
    msgs=P("""
what's the door code|question
how do i get the keys, arriving late|multi_sentence,question
lockbox code isnt working|indirect
self check in instructions for {bk}|entity
i'm outside the building, how do i get in|multi_sentence,question
key box code?|short
where is the key hidden|question
no one sent me the entry code and i'm standing in the rain|angry,multi_sentence
acess code for flat|typo,short
hi, which floor and which door is our apartment? and the code?|multi_sentence,question
can you resend the checkin instructions|question
the smart lock app says access denied|indirect
gate code for the villa|short
how do we collect keys after 10pm|question
do i need to meet the host for the keys|question
code for the building entrance?|short
i got the code but it's not opening the door|multi_sentence,indirect
where do i drop the keys when i leave|question
please share arrival instructions for {name}|polite,entity
""")),
}
HOTEL_EXTRA_MISSING = P("""
do you have a conference room for a meeting of 20 people|missing_intent,question
can you book me a taxi to the airport|missing_intent
any good restaurants nearby you recommend|missing_intent
is the hotel hiring? i want to apply|missing_intent,multi_sentence
can i buy a gift voucher for a stay|missing_intent
do you do wedding packages|missing_intent,question
can you arrange a city tour for us|missing_intent
i want to leave a review about my stay|missing_intent
do you have luggage storage after checkout|missing_intent,question
is there a shuttle bus from the airport|missing_intent,question
""")
HOTEL_CONFLICTS = [("checkin_checkout_times", "early_late_request"), ("security_deposit", "refund_status"),
                   ("modify_reservation", "new_booking"), ("amenities", "room_issue"), ("amenities", "housekeeping_request"),
                   ("room_issue", "access_instructions"), ("directions_location", "access_instructions"),
                   ("room_issue", "housekeeping_request"), ("checkin_checkout_times", "access_instructions")]

# cross-domain off-topic: intents that cannot fit any path of the other domain
CROSS_TO_HOTEL = ["flight_status", "baggage_allowance", "web_checkin", "seat_selection", "delay_compensation"]
CROSS_TO_AIR = ["parking", "housekeeping_request", "access_instructions", "room_issue", "amenities"]

GIBBERISH = P("""
qwewqeqw|gibberish,short
asdf|gibberish,short
...|gibberish,short
asdfghjkl|gibberish,short
jjjjjj|gibberish,short
???|gibberish,short
zxcvb|gibberish,short
lkjhg fds|gibberish,short
12345|gibberish,short
aaaaaaa|gibberish,short
mnbvc qwe rty|gibberish,short
..,..|gibberish,short
xcvxcv|gibberish,short
ppppp|gibberish,short
dfgdfg hjk|gibberish,short
qwerty|gibberish,short
!!!|gibberish,short
sdkfjh sdkjf wer|gibberish,short
1111|gibberish,short
wqeqwe asd|gibberish,short
kjasdh|gibberish,short
hjhjhj|gibberish,short
bnm bnm bnm|gibberish,short
.|gibberish,short
ghfjdk slal qpwo|gibberish
""")
FILLER_ALWAYS = P("""
hmm|short
umm|short
lol|short,slang
yes|short
no|short
hmmm ok so|short
wait|short
""")
FILLER_NO_THANKS = P("""
ok|short
okay|short
k|short
alright|short
sure|short
""")
OFFTOPIC = P("""
what's the weather in london tomorrow|off_topic
write me a poem about cats|off_topic
who won the football last night|off_topic,question
what is 25 times 4|off_topic,question
tell me a joke|off_topic
can you help with my maths homework|off_topic,question
recommend a good netflix series|off_topic
how do i bake banana bread|off_topic,question
what's the capital of australia|off_topic,question
translate hello into french|off_topic
is bitcoin going up this week|off_topic,question
my laptop wont turn on, help|off_topic
how tall is mount everest|off_topic,question
play some music|off_topic
can you write my cover letter|off_topic
give me a workout plan|off_topic
what time is it in tokyo|off_topic,question
sing me a song|off_topic
how to lose weight fast|off_topic
who painted the mona lisa|off_topic,question
i need a plumber for my house|off_topic
best laptop for students?|off_topic,question
""")


# ---------------------------------------------------------------- workflows
AIR_WF = [
    ("air_skyline_support", "examples", ["greeting", "flight_status", "book_flight", "change_flight", "cancel_booking",
                                         "refund_status", "baggage_allowance", "lost_baggage", "talk_to_human", "thanks_goodbye"], {}),
    ("air_budget_carrier", "desc", ["flight_status", "web_checkin", "seat_selection", "baggage_allowance", "delay_compensation"],
     {"flight_status": "check_flight", "web_checkin": "online_checkin"}),
    ("travel_agency_trips", "mixed", ["book_flight", "change_flight", "cancel_booking", "refund_status", "travel_docs", "invoice", "talk_to_human"],
     {"book_flight": "new_trip", "travel_docs": "visa_and_passport"}),
    ("air_premium_club", "examples", ["greeting", "loyalty_points", "seat_selection", "special_assistance", "pet_travel",
                                      "web_checkin", "lost_baggage", "thanks_goodbye"], {"loyalty_points": "miles_enquiry"}),
    ("air_regional_hops", "desc", ["flight_status", "delay_compensation", "refund_status", "talk_to_human"], {"talk_to_human": "agent"}),
]
HOTEL_WF = [
    ("hotel_city_central", "examples", ["greeting", "new_booking", "modify_reservation", "cancel_reservation", "checkin_checkout_times",
                                        "early_late_request", "amenities", "parking", "talk_to_human", "thanks_goodbye"], {}),
    ("rentals_homeshare", "desc", ["access_instructions", "security_deposit", "refund_status", "cancel_reservation", "room_issue", "lost_item"],
     {"access_instructions": "self_checkin_help", "room_issue": "report_problem"}),
    ("resort_beachside", "mixed", ["greeting", "new_booking", "amenities", "housekeeping_request", "room_issue", "pet_policy",
                                   "directions_location", "invoice"], {"housekeeping_request": "room_service_request"}),
    ("hostel_budget_stay", "desc", ["checkin_checkout_times", "directions_location", "lost_item", "invoice"], {"lost_item": "lost_and_found"}),
    ("serviced_apartments", "examples", ["modify_reservation", "cancel_reservation", "refund_status", "security_deposit",
                                         "access_instructions", "early_late_request", "talk_to_human", "thanks_goodbye"], {}),
]

TYPO_OPS = ("swap", "drop", "double")


def typo(text, rng):
    words = text.split()
    idx = [i for i, w in enumerate(words) if len(w) >= 4 and w.isalpha()]
    if not idx:
        return None
    i = rng.choice(idx); w = words[i]; j = rng.randrange(1, len(w) - 1); op = rng.choice(TYPO_OPS)
    words[i] = (w[:j] + w[j + 1] + w[j] + w[j + 2:]) if op == "swap" else (w[:j] + w[j + 1:]) if op == "drop" else (w[:j] + w[j] + w[j:])
    return " ".join(words)


def fill(t, rng):
    used = {}
    def sub(m):
        k = m.group(1)
        opts = [v for v in FILL[k] if v not in used.values()]
        used[k] = rng.choice(opts)
        return used[k]
    return re.sub(r"\{(\w+)\}", sub, t)


def mk(t, tags, gold, rng):
    tags = list(dict.fromkeys(tags + (["entity"] if "{" in t else [])))
    txt = fill(t, rng)
    if len(txt.split()) <= 3 and "short" not in tags:
        tags.append("short")
    return {"text": txt, "gold": gold, "tags": tags}


def path_text(spec, style, rng):
    if style == "desc":
        return spec["desc"][: rng.choice([1, 2])]
    if style == "examples":
        return rng.sample(spec["ex"], min(len(spec["ex"]), rng.randint(5, 8)))
    return [spec["desc"][0]] + rng.sample(spec["ex"], rng.randint(2, 4))


def build(wf, intents, conflicts, extra_missing, cross, domain, source_tag, seed):
    wid, style, chosen, alias = wf
    rng = random.Random(seed)
    pid = {k: alias.get(k, k) for k in chosen}
    paths = [{"path_id": pid[k], "text": path_text(intents[k], style, rng)} for k in chosen]
    msgs = []
    for k in chosen:
        pool = intents[k]["msgs"]
        picked = [mk(t, tg, pid[k], rng) for t, tg in rng.sample(pool, min(20, len(pool)))]
        # augmentation to ~25: typo / lowercase-no-punct variants of other pool items
        seen = {m["text"].lower() for m in picked}
        tries = 0
        while len(picked) < 25 and tries < 100:
            tries += 1
            t, tg = rng.choice(pool)
            m = mk(t, tg, pid[k], rng)
            if rng.random() < 0.6:
                v = typo(m["text"], rng)
                if v: m["text"], m["tags"] = v, list(dict.fromkeys(m["tags"] + ["typo"]))
            else:
                m["text"] = re.sub(r"[?!.,]", "", m["text"]).lower()
            if m["text"].lower() not in seen:
                seen.add(m["text"].lower()); picked.append(m)
        msgs += picked
    # __none__
    none = [mk(t, tg, "__none__", rng) for t, tg in rng.sample(GIBBERISH, 6)]
    filler = FILLER_ALWAYS + ([] if "thanks_goodbye" in chosen else FILLER_NO_THANKS)
    none += [mk(t, tg, "__none__", rng) for t, tg in rng.sample(filler, 3)]
    none += [mk(t, tg, "__none__", rng) for t, tg in rng.sample(OFFTOPIC, 5)]
    for k in rng.sample(cross[0], 2):
        t, tg = rng.choice(cross[1][k]["msgs"])
        none.append(mk(t, list(dict.fromkeys(tg + ["off_topic"])), "__none__", rng))
    blocked = set(chosen)
    for a, b in conflicts:
        if a in chosen: blocked.add(b)
        if b in chosen: blocked.add(a)
    absent = [k for k in intents if k not in blocked]
    rng.shuffle(absent)
    miss = []
    for k in absent:
        for t, tg in rng.sample(intents[k]["msgs"], 2 if k not in ("greeting", "thanks_goodbye", "talk_to_human") else 1):
            miss.append(mk(t, list(dict.fromkeys(tg + ["missing_intent"])), "__none__", rng))
    rng.shuffle(miss)
    none += miss[:7]
    none += [mk(t, tg, "__none__", rng) for t, tg in rng.sample(extra_missing, 25 - len(none))] if len(none) < 25 else []
    seen = {m["text"].lower() for m in msgs}
    for m in none:
        if m["text"].lower() not in seen:
            seen.add(m["text"].lower()); msgs.append(m)
    rng.shuffle(msgs)
    return {"workflow_id": wid, "domain": domain, "source": source_tag, "paths": paths, "messages": msgs}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [("synth_2_a.jsonl", AIR_WF, AIR, AIR_CONFLICTS, AIR_EXTRA_MISSING, (CROSS_TO_AIR, HOTEL), "airline_travel"),
            ("synth_2_b.jsonl", HOTEL_WF, HOTEL, HOTEL_CONFLICTS, HOTEL_EXTRA_MISSING, (CROSS_TO_HOTEL, AIR), "hotels_rentals")]
    allrecs = []
    for fn, wfs, intents, conf, extra, cross, domain in jobs:
        recs = [build(wf, intents, conf, extra, cross, domain, "synthetic_v1", seed=i * 7919 + len(fn))
                for i, wf in enumerate(wfs)]
        blob = json.dumps(recs).lower()
        assert not any(f in blob for f in FORBIDDEN), "forbidden eval phrasing"
        assert not re.search(r"insurance|telecom|sim card|data plan|recharge", blob), "held-out domain leak"
        for r in recs:
            ids = {p["path_id"] for p in r["paths"]} | {"__none__"}
            assert all(m["gold"] in ids and m["tags"] for m in r["messages"]), r["workflow_id"]
            texts = [m["text"].lower() for m in r["messages"]]
            assert len(set(texts)) == len(texts), (r["workflow_id"], [t for t in texts if texts.count(t) > 1])
        (OUT / fn).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs))
        allrecs += recs
        for r in recs:
            n = sum(m["gold"] == "__none__" for m in r["messages"])
            print(f"{fn} {r['workflow_id']:24s} paths={len(r['paths']):2d} msgs={len(r['messages']):3d} none={n}")
    if "--check" in sys.argv:
        rng = random.Random(1)
        flat = [(r["workflow_id"], m) for r in allrecs for m in r["messages"]]
        for wid, m in rng.sample(flat, int(sys.argv[sys.argv.index("--check") + 1])):
            print(f"[{wid}] {m['gold']:22s} {m['text']!r} {m['tags']}")


if __name__ == "__main__":
    main()
