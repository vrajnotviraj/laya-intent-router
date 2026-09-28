"""E-commerce retail workflows for synth_0_a. Lines are 'text|tag,tag'."""

WORKFLOWS = [
# ---------------------------------------------------------------- fashion, mixed phrasing style
dict(id="synth0a_threadline_apparel", paths={
    "greeting": ["hi", "hello", "hey there", "good morning"],
    "size_guide": ["Customer wants help choosing the right size or wants the size chart", "what size should i get", "size chart please"],
    "exchange_size": ["exchange for a different size", "Customer wants to swap an item they bought for another size or colour", "this is too small can i get a bigger one"],
    "return_request": ["I want to send this back", "Customer wants to return an item for a refund", "start a return"],
    "refund_status": ["where is my refund", "Customer already returned or cancelled something and asks when the money will be credited"],
    "track_shipment": ["track my parcel", "when will my order arrive", "Customer asks where their shipment is"],
    "apply_coupon": ["Customer has a discount code or promo code question", "how do i use my coupon", "promo code"],
    "talk_to_human": ["talk to an agent", "I want a real person", "connect me to customer support"],
}, msgs={
"greeting": """
hi|short
hii|short,slang
hello!|short
hey|short
good morning|short,polite
gm|short,slang
heyy there|short,slang
hello threadline|short
yo|short,slang
hiya|short,slang
good evening|short,polite
helo|short,typo
hey team|short
hi :)|short
hello good afternoon|polite
hey hey|short
morning!|short
hi there|short
heloo|short,typo
hey how are you|question
hi i'm Priya|short,entity
greetings|short,polite
hey, hope you're well|polite
hello??|short
hi there team|short
""",
"size_guide": """
what size should i order for a 32 waist|question,entity
im 5'8 and 70kg, M or L in the linen shirt?|question,entity
do your jeans run small|question
size chart for dresses pls|short
is the Aria dress true to size|question,entity
whats the diffrence between S and M in the hoodie|typo,question
i usually wear a UK 8, what's that in your sizes|entity,question
my chest is 40 inches which size fits|entity
not sure about sizing, can you help before i buy|polite
sizng guide|typo,short
how do i measure myself for the blazer|question
between two sizes for the trench coat, go up or down?|question
are the shoe sizes EU or US|question
hey does the oversized tee fit big or should i size down|slang,question
can u send me the measurements for the cargo pants in XL|entity,slang
what's the inseam on the 30 regular chinos|entity,question
I don't want to order wrong again. Which size would suit me at 165cm?|multi_sentence,entity
kids size chart for age 6-7|entity,short
hip measurement for size 10 skirt?|entity,short
do u have a fit guide for the slim fit jeans|question
is a large going to be baggy on me, im pretty skinny|slang,question
Hello, could you kindly share the size chart for women's tops?|polite
bra size conversion??|short,question
M is usually tight on my shoulders, what should I pick in the new bomber jacket|indirect
which size is right for a 10 year old in the school shorts|entity,question
""",
"exchange_size": """
the jeans i got are too tight can i swap for a 34|entity
exchange order #TL-55120 for size L|entity
got the dress in S, need M instead|short
can i exchange this for a different colour|question
the shirt fits weird, i want the same one in a bigger size|indirect
swap size pls, order 88213|entity,short
exchnage for smaller size|typo,short
Hi, I received my sneakers but they are half a size too big. Can I get them in 8.5 instead?|multi_sentence,polite,entity
i ordered black but i'd rather have the navy one, same size|indirect
how do i exchange a hoodie|question
this top is way too baggy, I'd like to exchange it for an XS|entity
i picked the wrong size, want a 10 instead, dont want my money back|entity
can i change the size of the trousers I got yesterday|question
the kids tshirt is too small for my son, can i get age 8-9 instead|entity
Is it possible to swap the white linen shirt for the beige one?|polite,question
ugh the pants are huge on me, gimme a smaller size|angry,slang
do exchanges cost anything? i want a bigger size|question,multi_sentence
i want to swap my order AB-4471 for size 42 shoes|entity
tried it on. sleeves too short, need L instead of M|multi_sentence
exchange for different size|short
can i trade these for the next size up|slang,question
Good afternoon, I'd like to exchange my jacket for a medium please|polite
the colour looks off in person, can i get the green one instead|indirect
size swap for order no 71023|entity,short
the blazer is fine but i need it one size down, exchange please|polite
""",
"return_request": """
i want to return the jacket|short
how do i send back an item|question
return order #TL-60431|entity,short
dont like the fabric, want to send it back and get my money|indirect
start a return for the linen trousers|short
honestly the colour is nothing like the pictures, i want to return it|angry
can i return something i bought on sale|question
retrun request|typo,short
I changed my mind about the coat. Can I send it back for a refund?|polite,question,multi_sentence
how many days do i have to return stuff|question
need to return 2 items from order 44871|entity
I'd like to return the dress, it doesn't suit me. Not interested in an exchange.|polite,multi_sentence
return pickup for my order pls|short
can i return without the tags|question
this is poor quality, i want to return it immediately|angry
bought a gift for my sister and she doesn't want it, how do i return it|question
refund and return the shoes please, dont want a replacement|polite
hey so i want to give back the hoodie i ordered|slang
Return label please for order TL-10293|entity
the stitching came apart after one wash. I want to return it|multi_sentence
can i drop the return off at a store instead of courier|question
wanna return these jeans|slang,short
returning 1 of 3 items from my last order, how|question
I bought it on the 12th of May, still able to return?|entity,question
package arrived fine but i dont need it anymore, want to return it|indirect
""",
"refund_status": """
where is my refund|short,question
i returned the jeans 10 days ago and still no money|indirect,entity
refund status for order #TL-60431|entity
when will i get my money back, return was picked up on Monday|entity,question
the courier collected the return last week, refund still not in my account|indirect
its been 2 weeks since my return, where is my 2,499|entity,angry
hows my refund coming along|slang,question
refund not received yet|short
did you process my refund? return ID RT-9921|entity,question
Hi, I sent back a dress on 3 June. Could you tell me when the refund will be credited?|polite,multi_sentence,entity
you guys received my return, why no refund yet|angry,question
refnd still pending|typo,short
how long do refunds take to show on the card|question
my bank says nothing has come in from you for the return i made|indirect
cancelled order 55821 but money not back yet|entity
waiting on a refund of $45|entity
any update on the refund please|polite,short
the app says refund initiated but i see nothing|indirect
already returned it. is the refund going to my card or store credit?|question,multi_sentence
return done, money when?|short,slang
seriously its been a month and still waiting for my refund|angry
please check refund for Rohan Mehta, phone 98201 44512|entity
refund status??|short
I got an email saying return received, when does the refund come through|question
my refund was approved 5 days ago but hasn't landed|indirect,entity
""",
"track_shipment": """
where's my order #TL-77012|entity,question
when will my hoodie arrive|question
ordered on friday, still not shipped?|question,entity
has my package been dispatched|question
tracking number please for order 30912|entity,polite
hi, i ordered shoes last week, still nothing, where is it|multi_sentence
wheres my stuff|slang,short
trak order|typo,short
it's been 6 days and my order hasnt moved from the warehouse|indirect,angry
Could you share an update on my delivery please?|polite
is my package out for delivery today|question
the tracking link isn't updating, where is the parcel|indirect
expected delivery date for AB-4471?|entity,question
my order is late, it was supposed to come yesterday|indirect
which courier is delivering my order|question
Hello, can you tell me when my jacket will be delivered? I need it by Saturday|polite,multi_sentence,entity
still waiting on my delivery ugh|angry,slang
order status 81123|entity,short
will my order reach Pune by the 20th|entity,question
what's the ETA on my package|slang,question
my parcel says in transit for 4 days now|indirect,entity
shipment update pls|short
is it shipped yet|short,question
the delivery date keeps changing, when is it actually coming|angry,question
can you check where my dress order is|question
""",
"apply_coupon": """
how do i use my coupon|question
promo code WELCOME10, not sure where to enter it|entity
do you have any discount codes right now|question
is there a coupon for first order|question
can i use two promo codes together|question
my code SUMMER20 says invalid|entity
forgot to apply my discount code at checkout, can you still add it|indirect
cupon code|typo,short
where do i put the voucher code|question
the 15% off from the email didn't apply|indirect,entity
promo code for students?|question,short
got a gift card code FASH-8812, how to redeem|entity
does the birthday discount work on sale items|question
Hi! I have a referral code from my friend. How do I use it?|polite,question,multi_sentence
code not working!! tried 3 times|angry
is FREESHIP still valid|entity,question
can u give me a discount code pls|slang,polite
coupon expired yesterday can you extend it|entity
min order value for the coupon?|short,question
Does the NEWYEAR25 code apply to accessories as well?|entity,question
i saw a 20% off code on instagram but it doesnt work|indirect
apply coupon|short
any promo codes for the jeans sale|question
the discount code removed itself when i went to payment|indirect
is there a code for free delivery|question
""",
"talk_to_human": """
talk to an agent|short
i want to speak to a real person|short
connect me to customer care|short
is there a human i can chat with|question
agent pls|short
this bot is useless, get me a person|angry
can someone from your team call me on 9876543210|entity
stop the bot, i need a human|angry
hello, can I talk to a support executive please?|polite
customer service number?|short,question
live chat with a person|short
i need to talk to somebody about a problem|indirect
put me through to a manager|short
speak to human|short
humn agent|typo,short
you're not understanding me, I want a real person|angry
can i get a callback from support|question
Is there anyone available to talk to?|polite,question
representative|short
I'd prefer to explain this to a person rather than a bot|polite,indirect
transfer me to support staff|short
real person plz|slang,short
Call me back please, my name is Anjali, 91 99887 76655|entity,polite
need help from an actual human being|short
escalate this to someone senior|indirect
""",
"__none__": """
qwewqeqw|gibberish
asdfgh|gibberish
...|gibberish,short
kjhkjh lol|gibberish
ok|short
hmm|short
what's the weather in Mumbai today|off_topic,entity
write me a poem about the sea|off_topic
who won the match last night|off_topic
tell me a joke|off_topic
do you sell sofas?|missing_intent,question
what are your store opening hours|missing_intent,question
how do i delete my account|missing_intent
I want to update my email address on my profile|missing_intent
are you hiring? i want to apply for a job|off_topic
my payment failed while ordering|missing_intent
do you ship to Canada|missing_intent,entity
how do i change my password|missing_intent
zzzzzz|gibberish
lorem ipsum dolor|gibberish
what is 25 times 17|off_topic
recommend a good movie|off_topic
can i gift wrap my order|missing_intent
i want to sell my clothes on your site|missing_intent
sdfkj sdkfj ekjr|gibberish
test|short
""",
}),

# ---------------------------------------------------------------- electronics, description-only style
dict(id="synth0a_voltkart_electronics", paths={
    "payment_failed": ["Customer's payment failed or money was deducted but the order did not go through"],
    "damaged_on_arrival": ["Customer received a product that was broken, damaged or not working right out of the box"],
    "warranty_repair": ["Customer's device stopped working after some time of use and they want a repair or service under warranty"],
    "track_order": ["Customer asks when their electronics order will be delivered", "Customer wants a shipping update"],
    "cancel_before_shipping": ["Customer wants to cancel a purchase that has not shipped yet"],
    "invoice_request": ["Customer needs a bill, tax invoice or receipt for a purchase"],
    "installation_booking": ["Customer wants to schedule installation or a demo of an appliance like an AC, TV or washing machine"],
}, msgs={
"payment_failed": """
payment failed but money got deducted|short
i paid 54,999 and the order isnt showing|entity,indirect
card declined at checkout, why?|question
transaction failed twice for the laptop order|entity
UPI payment stuck on pending for 30 min|entity
money cut from my account, no order confirmation|indirect
my payment didnt go through|short
payment faild|typo,short
Hi, I tried to pay for the headphones and it failed, but my bank shows a debit of Rs 3,499. Please help|multi_sentence,polite,entity
why does my card keep getting rejected on your site|angry,question
double charged for one order!! txn ID TXN88213|angry,entity
EMI payment error when buying the tablet|short
the payment page just froze and now i see the amount gone from my wallet|indirect
checkout keeps saying payment unsuccessful|indirect
netbanking failed but amount debited on 14 Aug|entity
did my payment go through? i didnt get any email|question,indirect
tried paying with Amex, got error code 502|entity
my order got stuck at payment|short
You took my money and there's no order. Fix this|angry,multi_sentence
payment unsuccesful pls check|typo
how long until a failed payment is reversed to my card|question
cant complete payment for the smartwatch|short
split payment with gift card and wallet failed|indirect
Is there an issue with your payment gateway? It failed three times now|question,multi_sentence
money deducted order not placed|short
""",
"damaged_on_arrival": """
the tv screen arrived cracked|short
box was crushed and the speaker inside is broken|indirect
laptop came with a dent on the lid|short
received damaged item order #VK-30219|entity
opened the parcel and the mixer jar is shattered|indirect
my monitor has a broken corner straight out of the box|indirect
delivery guy dropped it i think, the fridge door is dented|indirect
the headphones came with one ear cup snapped off|short
Hello, the microwave I received yesterday has a crack in the glass door. What can I do?|polite,multi_sentence,question
damged product recieved|typo,short
arrived broken!!!|angry,short
just got the charger today and the cable is already torn|indirect
unboxed my new keyboard and several keys are missing|indirect
screen shows lines from the very first time i switched it on|indirect
the washing machine was delivered with a scratched body and a broken knob|short
got my order 77120 today and the camera lens is cracked|entity
seriously, a brand new tablet with a shattered screen??|angry
the package was soaked and the printer inside won't start|indirect
item damaged in transit|short
AC unit came with bent fins and a leaking pipe on delivery|short
the earbuds case arrived with a broken hinge|short
new air fryer arrived and the basket handle is snapped|short
vacuum cleaner delivered an hour ago, pipe is cracked, what now|question,entity
brand new speaker, just unboxed, doesnt turn on at all|indirect
Please help, the TV I got on 2nd Oct has a broken stand|polite,entity
""",
"warranty_repair": """
my laptop stopped charging after 4 months|entity
the tv I bought last year has no sound now|indirect
headphones stopped working, still under warranty?|question
need a repair for my fridge, not cooling since last week|short
warranty service for my washing machine, drum making noise|short
the mixer worked fine for 3 months and now it won't turn on|entity
how do i get my smartwatch repaired under warranty|question
AC not cooling anymore, bought from you in March|entity
my speaker battery dies in 10 minutes now, it used to last all day|indirect
book a technician visit, microwave stopped heating after 6 months of use|entity
is my monitor covered by warranty? it flickers now after 8 months|question,entity,multi_sentence
warrenty repair|typo,short
the keyboard's space bar broke after a few weeks of normal use|indirect
screen started flickering on my tablet, had it for 6 months|entity
Hello, my vacuum cleaner lost suction after half a year. Can you arrange a service?|polite,multi_sentence
bought this printer in Jan and it jams every page now, total junk|angry,entity
serial no SN-4471-XK stopped working, needs servicing|entity,short
my earbuds left side stopped playing sound, they're 5 months old|entity
the camera shows an error after using it for a while, need it fixed|indirect
warranty ends next month and the laptop fan has gone loud, can you fix it|multi_sentence
repair request for my iron, it stopped heating after a year|short
the geyser we bought from voltkart 7 months back leaks now|indirect,entity
it was working great until yesterday, now the air fryer doesnt heat|indirect
can i get it serviced for free? the blender motor burnt out after 2 months|question,entity,multi_sentence
my 1 year old TV has a dead pixel line now|entity
""",
"track_order": """
when will my laptop be delivered|question
order #VK-20931 shipping update|entity
has my tv been shipped yet|question
where is my package|short,question
it said 3-5 days, it's day 7|indirect,entity
tracking id for my headphones order?|question
deliverry date for my fridge|typo
is my order out for delivery today|question
Hi, can you tell me the delivery status of my monitor order please?|polite
still waiting for my speaker, ordered on 2 Sept|entity
my air fryer order hasn't moved from 'packed' for 3 days|indirect,entity
wheres my stuff man|slang
why is my delivery so late|angry,question
expected arrival for order 99812?|entity,question
ship status|short
which courier has my parcel|question
will the TV reach before the weekend|question
track|short
I need the smartwatch by friday for a gift. Will it arrive in time?|multi_sentence,question,entity
the tracking page shows no updates since monday|indirect
can you check where order VK-55012 is|entity
my order was supposed to come yesterday, still nothing|indirect
order update please|polite,short
delivery status|short
how far is my parcel from Bangalore|entity,question
""",
"cancel_before_shipping": """
cancel my order|short
i want to cancel the laptop i ordered an hour ago|entity
please cancel order #VK-40188|entity,polite
changed my mind, dont ship the tv|indirect
cancel before it ships pls|short
canel order|typo,short
can i still cancel? i ordered it this morning|question,multi_sentence
I found it cheaper elsewhere, cancel my purchase|indirect
stop my order from shipping|short
ordered the wrong model by mistake, cancel it|short
how do I cancel an order that hasnt been dispatched yet|question
cancel the headphones from my order, keep the rest|short
Hi, I'd like to cancel my order placed on 3rd Sept. Thanks|polite,entity,multi_sentence
i dont want it anymore, please cancel before shipping|polite
cancel it now!!! i placed it by accident|angry
is there a cancellation fee|question
my order 60021 still says processing, cancel it|entity
want to cancel, bought 2 by mistake need only 1|entity
kindly cancel the washing machine order, we are moving house|polite
cancellation request|short
dont send the air fryer, cancel please|polite
accidentally placed the order twice, cancel one of them|indirect
cancel order for Rahul, phone 9820012345|entity
the delivery date is too late for me, just cancel|indirect
nah cancel it|slang,short
""",
"invoice_request": """
need the invoice for my laptop|short
send me the bill for order #VK-11873|entity
gst invoice please|short,polite
can I get a receipt for my purchase|question
my company needs a tax invoice with our GSTIN 27AAACB1234F1Z5|entity
where do i download the invoice|question
invoice not in the box|short,indirect
invoce for tv|typo,short
Hi, could you email me the invoice for my order from 12 July?|polite,entity
i need the bill for my office reimbursement|indirect
the invoice has the wrong name, please correct it to Neha Sharma|entity
can you add my company name on the invoice|question
duplicate bill needed, lost the original|short
invoice copy pls|short
my accountant is asking for the purchase receipt|indirect
please resend the invoice to vk.buyer@gmail.com|entity
where's my bill?? paid 3 weeks ago|angry,question
I didn't get any invoice email after buying the headphones|indirect
need a proper tax invoice not just order confirmation|short
bill for order 88213 please|entity,polite
can u send the receipt on whatsapp|question,slang
proforma invoice before i pay for the bulk order|short
billing address is wrong on my invoice|indirect
the pdf invoice won't open, send again|indirect
receipt|short
""",
"installation_booking": """
book installation for my AC|short
when will someone come to install the tv|question
need a demo for the washing machine delivered today|short
schedule wall mounting for my 55 inch TV|entity
installation request order #VK-66102|entity
the dishwasher arrived, who installs it|question,indirect
can the technician come on Sunday for installation|entity,question
instalation for water purifier|typo
Hi, my new split AC was delivered yesterday. Please arrange installation.|polite,multi_sentence
its been 3 days, nobody came to fit the chimney|angry,indirect
do you provide free installation for geysers|question
i want to book a demo of the robot vacuum|short
set up appointment for fridge installation|short
wall mount install tomorrow morning possible?|question
the installer didn't show up today, rebook please|indirect
can someone set up the home theatre system|question
install my washer pls, flat 4B, Green Park|entity
installation charges for the microwave?|question
book technician for AC fitting at 10am on 5 Oct|entity
Need an installer for the ceiling fan I bought|short
how do i book the free demo that came with the TV|question
please send someone to install the oven|polite
who do i contact for installation|question
install appointment|short
installation still pending for order 70231|entity
""",
"__none__": """
asdfasdf|gibberish
..........|gibberish,short
hmm ok|short
ok thanks|short
what's the capital of france|off_topic
write python code to sort a list|off_topic
can you recommend a laptop under 50k|missing_intent
do you have the new iPad in stock|missing_intent,entity
I want to return my headphones, I don't like them|missing_intent
where's my refund|missing_intent
how do i change my delivery address|missing_intent
do you have an exchange offer on my old tv|missing_intent
xcvbnm|gibberish
123123|gibberish
lol|short
play some music|off_topic
what's the bitcoin price|off_topic
is it going to rain tomorrow|off_topic
tell me about yourself|off_topic
do you price match amazon|missing_intent,entity
gjhgjhg hghj|gibberish
hi|short
I want to become a seller|missing_intent
k|short
translate hello to spanish|off_topic
""",
}),

# ---------------------------------------------------------------- furniture, short example utterances
dict(id="synth0a_homenest_furniture", paths={
    "reschedule_delivery": ["change my delivery date", "reschedule delivery", "can you deliver on another day", "not home that day", "move my delivery slot", "deliver next week instead"],
    "assembly_service": ["need someone to assemble the bed", "assembly service", "do you assemble furniture", "book a carpenter for fitting", "help putting the wardrobe together"],
    "return_pickup": ["return this sofa", "schedule a return pickup", "i want to send the table back", "pick up the item for return", "return my chair"],
    "refund_status": ["refund status", "when will i get my money", "refund not received", "where is my refund", "money not credited"],
    "thanks_goodbye": ["thanks", "thank you", "bye", "that's all", "ok thanks bye", "great, thanks for the help"],
}, msgs={
"reschedule_delivery": """
can you deliver the sofa on saturday instead|entity
i wont be home on the 14th, move my delivery|entity
reschedule delivery pls|short
change delivery date for order #HN-2231|entity
deliver next week, the flat isnt ready yet|indirect
is it possible to push my bed delivery by 3 days|question,entity
My delivery is tomorrow but I'm travelling. Can we change it?|multi_sentence,question
resceduled delivery to evening please|typo
move my slot to after 6pm|entity
Hello, could you please reschedule my dining table delivery to Monday?|polite,entity
we're renovating, hold the wardrobe delivery till the end of the month|indirect
can the delivery come earlier, like thursday|question,entity
nobody will be home on friday for the drop|indirect,entity
i need a different delivery day|short
postpone delivery|short
the delivery time you gave clashes with work, change it|indirect
deliver on 2 Nov not 28 Oct|entity
can u deliver sunday?|slang,short,question
delivery date change needed, order 55901|entity
Pls shift the delivery of my mattress to next weekend|polite,entity
ugh you gave me a weekday slot, i need a weekend one|angry
Delivery on the 5th doesn't work anymore. What other dates are there?|multi_sentence,question
change the time of delivery|short
my building doesn't allow deliveries on sundays, please reschedule|indirect
rebook my delivery slot|short
""",
"assembly_service": """
need someone to assemble the king bed|short
do you guys assemble the wardrobe after delivery|question,slang
book assembly for order #HN-7812|entity
the bookshelf came in parts, can someone put it together|indirect
assembly service please|short,polite
how much does assembly cost for a 6 seater dining table|entity,question
asembly for study table|typo,short
Hi, is fitting of the TV unit included, or do I need to book it separately?|polite,question
the carpenter never came to put the bed together|angry,indirect
i cant figure out these instructions, send someone to build the cot|indirect
want a technician to mount the wall shelf|short
can the assembly be done on the same day as delivery|question
assemble the sofa cum bed pls|short
my dad's 70 and can't build the drawer unit himself, could someone come|indirect,polite
is there a fitting service for kitchen cabinets?|question
book a carpenter visit for tuesday 11am|entity
the shoe rack needs assembling|short
fitting for wardrobe, flat 902, Palm Heights|entity
i paid for assembly but nobody showed up|angry,indirect
can you put together the office chair when you drop it|question
bed assembly slot for tomorrow?|question,short
help assembling the bunk bed, order 33019|entity
Please arrange someone to assemble my furniture|polite
hey do u do assembly|slang,short
the wardrobe doors need to be fitted, can your team do it|question
""",
"return_pickup": """
return the sofa, it doesnt fit in my living room|indirect
schedule a pickup to return the coffee table|short
i want to send back the chair|short
return order #HN-4410|entity,short
the mattress is too firm, i want to return it|short
how do i return a big item like a bed|question
pick up the dining set for return pls|short
retrun pickup|typo,short
Hi, I'd like to return the wardrobe. When can you collect it?|polite,multi_sentence,question
the colour of the recliner doesn't match our room, please take it back|indirect
want to return the bookshelf within 7 days|entity
can your team come get the table on saturday, i'm returning it|entity
changed my mind about the ottoman, return it|short
not happy with the quality, arrange a pickup for return|angry
return request for 2 chairs|entity
the side table is wobbly, i dont want it, come take it|indirect,angry
book return collection|short
I'm returning the TV unit, what's the process?|question
we moved and the bed is too big now. Can I return it?|multi_sentence,question
take back the rug, it smells weird|indirect
return pls|short
return pickup for Aarav Shah, 98765 11223|entity
can i return the sofa even though i removed the plastic|question
the stools look cheap in person, I'd like to return them|polite
initiate return|short
""",
"refund_status": """
where is my refund for the returned sofa|question
the chair was picked up a week ago, no refund yet|indirect,entity
when will i get my 18,500 back|entity,question
refund not received for order #HN-4410|entity
you collected the table on Monday, money still not in my account|indirect,entity
how long does the refund take after pickup|question
refnd pending since 2 weeks|typo,entity
Hi, could you check the status of my refund? Return was completed on 10 Oct.|polite,multi_sentence,entity
its been 20 days, where's my money|angry,entity
return already done. refund to my card or bank?|question,multi_sentence
did the refund get processed|question
I cancelled the bed order and haven't got my money|indirect
money not credited yet|short
the return guy took the mattress, when do I get refunded|slang,question
update on my refund please|polite
still waiting on a refund for the stools|indirect
refund amount looks less than i paid, why|indirect,question
check refund, reference RF-22019|entity
you people are so slow with refunds|angry
my bank shows nothing from homenest yet|indirect
refund??|short
when does refund reflect in upi|question
my return was approved but refund not initiated|indirect
has my money been sent back|question
refund status|short
""",
"thanks_goodbye": """
thanks|short
thank you so much|polite
ok thanks bye|short
that's all for now|short
great, cheers|slang,short
bye|short
thx|slang,short
Thanks for the help, have a nice day!|polite
nothing else, thanks|short
ty|slang,short
perfect, thank you|polite,short
appreciate it|polite
got it, thanks a lot|short
tysm|slang,short
alright bye|short
thanks, that solved it|short
cool thanks|slang,short
many thanks|polite,short
thank u|short
ok that's it, bye bye|short
see ya|slang,short
thanks for sorting it out so quickly|polite
thnks|typo,short
goodbye|short
thank you, all good now|polite
""",
"__none__": """
wqeqwe|gibberish
hmm|short
???|gibberish,short
do you sell curtains|missing_intent
what is the warranty on the sofa|missing_intent
i want to change the colour of my order before it ships|missing_intent
payment failed on your website|missing_intent
can i pay in installments|missing_intent
where is your showroom in Delhi|missing_intent,entity
do you have a discount code|missing_intent
how do i clean a velvet sofa|missing_intent
recommend me a good book|off_topic
what time is it in London|off_topic,entity
write a birthday message for my mom|off_topic
how many calories in a banana|off_topic
jkjkjkjk|gibberish
aaaaaaaa|gibberish
hi|short
hello|short
my order hasn't arrived yet, where is it|missing_intent
lkjdsf 2323|gibberish
who is the prime minister of japan|off_topic
can you do my homework|off_topic
huh|short
..|gibberish,short
""",
}),

# ---------------------------------------------------------------- beauty subscription, mixed, 10 paths
dict(id="synth0a_glowbox_beauty", paths={
    "greeting": ["hi", "hello", "hey"],
    "loyalty_points_balance": ["how many points do I have", "Customer wants to check their GlowPoints balance or tier", "points balance"],
    "redeem_points": ["use my points", "Customer wants to spend or redeem loyalty points on an order", "convert points to discount"],
    "coupon_not_working": ["my promo code isn't working", "Customer says a coupon or discount code was rejected at checkout"],
    "pause_subscription": ["pause my box", "Customer wants to skip or pause their monthly beauty box temporarily but keep the subscription", "skip next month"],
    "cancel_subscription": ["cancel my subscription", "Customer wants to end their beauty box subscription permanently", "stop my membership"],
    "product_recommendation": ["what should i use for oily skin", "Customer wants product suggestions for their skin or hair type", "recommend a serum"],
    "ingredient_question": ["is this product vegan", "Customer asks about ingredients, allergens or whether a product is safe for them", "does it contain fragrance"],
    "track_package": ["where is my box", "Customer asks for delivery status of their order or monthly box"],
    "talk_to_human": ["chat with an agent", "human please"],
}, msgs={
"greeting": """
hi|short
hello|short
hey glowbox|short
hiii|slang,short
good morning!|polite,short
heyyy|slang,short
hi there|short
hello :)|short
hey girl|slang,short
good evening|polite,short
helloo|typo,short
hi, hope you're having a good day|polite
morning|short
hey hey|slang,short
hey!!|short
hi it's Meera|entity,short
hellooo glowbox team|slang
good afternoon|polite,short
yo|slang,short
hullo|typo,short
hey there, happy friday|short
heya|slang,short
hi team|short
greetings|polite,short
hello hello|short
""",
"loyalty_points_balance": """
how many points do i have|question
glowpoints balance|short
check my points please|polite,short
what tier am i on|question
how close am i to gold tier|question
points balance for account GB-20117|entity
my points look lower than last month, what's my current total|indirect,question
do my points expire? how many do i have left|question,multi_sentence
did i get points for my last order? what's my total now|question,multi_sentence
pionts balance|typo,short
Hi! Could you tell me my current loyalty points?|polite,question
how many points did i earn from order #GB-5512|entity,question
where can i see my rewards points|question
loyalty status?|short,question
points??|short
i'm registered with 98111 22334, how many points|entity
how much are my points worth right now|question
why do i only have 120 points|indirect,entity,question
show my reward points total|short
am i still a silver member|question
were my birthday points added? total please|question
total glowpoints?|short
how many points till my next free gift|question
points check for Riya Kapoor|entity
how many reward points have i got|question
""",
"redeem_points": """
use my points on this order|short
how do i redeem glowpoints|question
can i pay with points|question
convert 500 points to a discount|entity
i want to spend my points on the lipstick set|short
apply points at checkout|short
redem points|typo,short
Hi, I'd like to use my loyalty points for my next purchase. How?|polite,multi_sentence
the redeem points button is greyed out|indirect
i have 2000 points, want to use them for the serum|entity
exchange points for a free product|short
can i redeem points for the monthly box|question
points not getting applied when i try to redeem|indirect
use rewards|short
cash in my points plz|slang
redeem 300 points on order #GB-9910|entity
what can i get with my points|question
I want to use my GlowPoints before they expire|indirect
how many points do i need to redeem the travel kit|question
let me use points to pay for shipping|short
trade in my points for the mini kit|slang
spend points|short
Can I redeem points on sale items?|question
use all my points on the cart pls|slang
put my points towards the new palette|short
""",
"coupon_not_working": """
my promo code isn't working|short
code GLOW20 says invalid|entity
coupon rejected at checkout|short
the discount code from your email doesnt apply|indirect
why is WELCOME15 not working??|entity,angry,question
cupon not working|typo,short
it says code expired but the email said valid till 30th|indirect,entity
Hi, I tried the referral code my friend gave me but it shows an error.|polite,multi_sentence
entered the code and the price didn't change|indirect
BDAY25 doesn't work on my cart|entity
promo code error|short
your coupons are a scam, they never work|angry
discount code not getting applied|short
the influencer code SANYA10 is failing|entity
coupon says minimum order not met but my cart is 1,500|indirect,entity
code not valid for this product? which product then|question,multi_sentence
tried 3 codes none of them work|angry
Could you check why my coupon won't apply?|polite,question
voucher code rejected|short
free shipping code not working|short
the 10% off code keeps giving an error|entity
code invalid|short
it says this code has already been used but i never used it|indirect
first order discount code isn't applying|short
promo fail|slang,short
""",
"pause_subscription": """
pause my box for a month|short
skip next month's box|short
can i take a break from my subscription|question
i'm travelling in december, hold my box|entity,indirect
pause subscription|short
dont send me the june box, but keep my plan|entity
paus my box pls|typo,short
Hi, I'd like to skip the next two deliveries but keep my membership.|polite,entity
how do i pause without cancelling|question
put my subscription on hold till march|entity
money is tight this month, can i skip it|indirect
skip october|entity,short
I still have products from last month. Can I skip this one?|indirect,question,multi_sentence
freeze my plan for 2 months|entity
temporarily stop my box|short
can u pause it, i'll resume in a few weeks|slang
pause the beauty box for account GB-7781|entity
hold my next box, i'll continue after|short
i want a pause not a cancellation|short
skip a month please|polite,short
moving house, pause deliveries till I update the address|indirect
is there a way to snooze my subscription|question
pause the box, not cancel!!|angry
resume later, pause for now|short
don't charge me this month, i'll be back next month|indirect
""",
"cancel_subscription": """
cancel my subscription|short
i want to end my glowbox membership|short
stop my monthly box permanently|short
how do i cancel the beauty box|question
unsubscribe me from the box|short
cancle subscription|typo,short
Hi, please cancel my subscription effective immediately.|polite
i dont want the box anymore, cancel it|short
stop charging my card every month, i'm done|angry,indirect
cancel plan for account GB-3310|entity
I'd like to close my subscription, the products don't suit me|polite
end my membership|short
you charged me again, cancel this subscription now|angry
not renewing, cancel it|short
i'm quitting the box for good|slang,indirect
how to stop the auto renewal and end it|question
cancel sub|slang,short
I no longer want to be a subscriber|indirect
cancel the plan, registered number 98700 55443|entity
done with glowbox, cancel|slang,short
please terminate my monthly subscription|polite
Can I cancel before the next billing date on the 5th?|question,entity
remove me from the subscription permanently|short
stop my box forever|short
cancel my annual plan|short
""",
"product_recommendation": """
what should i use for oily skin|question
recommend a serum for dark spots|short
best moisturiser for dry skin in winter?|question
i have curly frizzy hair, what products do you suggest|question
suggest a sunscreen that doesnt leave a white cast|short
need a gift for my mom, she likes skincare|indirect
what's good for acne scars|question
reccomend a lipstick shade for dusky skin|typo
Hi, I'm 35 with combination skin. Could you suggest a night routine?|polite,multi_sentence,entity
which foundation would suit me, i'm NC30|entity,question
what shampoo for hair fall|short,question
i'm new to skincare, where do i start|indirect,question
top rated eye cream?|short,question
something for puffy eyes pls|slang,short
which perfume lasts longest|question
my skin gets super dry after washing, what cleanser should i buy|question
best budget kit under 1000|entity
what do you recommend for a beginner makeup kit|question
help me pick a toner|short
products for sensitive skin?|short,question
any good hair masks for bleached hair|question
looking for a vitamin c serum, which one|question
recommend me something for glowing skin before my wedding on 12 Dec|entity
what would you suggest for dandruff|question
need a lip balm recco|slang,short
""",
"ingredient_question": """
is the rose face mist vegan|entity,question
does the night cream contain retinol|question
is the GlowBox SPF 50 reef safe|entity,question
i'm allergic to nuts, does the shea butter lotion have nut oils|question
is your shampoo sulfate free|question
does the vitamin c serum have fragrance|question
ingrediants of the hair oil?|typo,short
Hi, is the peptide cream safe to use during pregnancy?|polite,question
is the lipstick cruelty free|question
full ingredient list for the clay mask please|polite
does the toner have alcohol in it|question
parabens in the body wash?|short,question
can i use the AHA exfoliant together with niacinamide|question
does the face wash contain salicylic acid|question
is the eyeliner safe for contact lens wearers|question
what's in the hair mask? i have a latex allergy|multi_sentence,question
does the kajal have lead in it|question
i reacted to the last cream, does the new one have lanolin too|indirect,question
is the lip scrub gluten free|question
what preservatives are used in the micellar water|question
does the sunscreen have oxybenzone?|question
is the serum halal certified|question
does the perfume contain essential oils? i get rashes|multi_sentence,question
is the body butter safe for a 3 year old|entity,question
conditioner is silicone free?|short,question
""",
"track_package": """
where is my box|short,question
has my august box shipped|entity,question
when will my order #GB-7721 arrive|entity,question
tracking link for my order please|polite
still havent received this month's box|indirect
my lipstick order hasnt come yet and it's been a week|indirect,entity
wheres my parcel|slang,short
trackng|typo,short
Hi, could you share the delivery status of my order?|polite
the courier status hasn't updated since tuesday|indirect,entity
my box usually comes by the 5th, it's the 9th|indirect,entity
delivery update|short
is my package out for delivery|question
why is my order taking so long|angry,question
which courier has my box|question
order status for Kavya, 90909 11122|entity
will the gift set reach by saturday|entity,question
package stuck in transit|short
i ordered the serum on monday, when does it get here|entity,question
where's my stuff??|slang,angry
has my order been dispatched yet|question
tracking says delivery tomorrow, is that right|question
how far away is my box|question
expected delivery date?|short
the box is late again!!|angry
""",
"talk_to_human": """
chat with an agent|short
human please|short
i want to talk to a real person|short
connect me to customer support|short
agent|short
can i speak to someone from the team|question
the bot isnt helping, get me a person|angry
live agent pls|short
Hi, could someone from customer care call me on 99001 12233?|polite,entity
talk to human|short
i need a human not a robot|angry
representative please|polite,short
is there a person i can chat with|question
transfer to agent|short
huamn agent|typo,short
let me talk to your support team|short
i want to complain to a real person|angry
escalate to a manager|short
someone call me back plz|slang
real human|short
need to speak with customer service|short
this is going nowhere, agent now|angry
can I get a real person on chat?|question
support team please|short
I'd rather talk to someone directly|polite,indirect
""",
"__none__": """
qwerty|gibberish
asdlkfj|gibberish
ok|short
hmm|short
k|short
what's the weather like|off_topic
write me a love poem|off_topic
how do i make pasta|off_topic
who is taylor swift dating|off_topic
my product arrived damaged|missing_intent
i want to return the lipstick|missing_intent
change my delivery address|missing_intent
how do i update my payment card|missing_intent
do you ship internationally|missing_intent
where is my refund|missing_intent
can i gift a subscription to my friend|missing_intent
zxzxzx|gibberish
!!!!|gibberish,short
lol ok|short
what is 2+2|off_topic
tell me a fun fact|off_topic
dfgdfg dfg|gibberish
my payment failed|missing_intent
what's your favourite colour|off_topic
sure|short
""",
}),

# ---------------------------------------------------------------- marketplace, 4 paths, mixed
dict(id="synth0a_shelfy_marketplace", paths={
    "contact_seller": ["Customer wants to message or contact the seller of a product", "ask the seller a question"],
    "report_counterfeit": ["this is a fake product", "Customer believes the item they got is counterfeit, a replica or not genuine"],
    "refund_status": ["refund status", "Customer asks when money for a returned or cancelled order will reach them"],
    "login_issue": ["can't log in", "Customer can't sign in, didn't get the OTP, or forgot their password"],
}, msgs={
"contact_seller": """
how do i contact the seller|question
can i ask the seller if this comes in blue|question
message seller about order #SH-44012|entity
i want to talk to the shop that sold me the watch|indirect
seller phone number?|short,question
does the seller do custom engraving? how can i ask them|question,multi_sentence
contct seller|typo,short
Hi, I'd like to ask the seller about bulk pricing. How do I reach them?|polite,multi_sentence,question
the seller hasn't replied to my question for 3 days|indirect,entity
i need to ask the vendor about the size of the rug|short
can you connect me with the seller 'UrbanCraft'|entity
where's the chat with seller option|question
seller not responding to my messages|short
i want the seller to add a gift note|indirect
how do i ask the seller for more photos|question
reach out to seller|short
ask the seller if the bulb is included with the lamp|short
message the store directly|short
is there a way to get in touch with the merchant|question
the listing says 'ask seller for details', how|indirect,question
pls connect me to the seller of order 77231|entity,polite
seller contact info|short
i have a question for the seller before i buy|short
want to negotiate the price with the seller|short
can the seller ship it faster? how do i ask|question,multi_sentence
""",
"report_counterfeit": """
this is a fake product|short
the perfume i got is a replica, not original|short
report counterfeit sneakers|short
the watch doesn't look genuine, the logo is wrong|indirect
i think the handbag is a first copy|indirect
not authentic!! i want to report this seller|angry
fake airpods sold to me in order #SH-90012|entity
counterfit item|typo,short
Hello, the serial number on the headphones doesn't match the brand's site. I think it's fake.|polite,multi_sentence
the hologram sticker is missing, it's a duplicate|indirect
how do i report a fake listing|question
you sold me a knockoff|angry,slang
brand verification failed for my shoes, they're counterfeit|short
the packaging is misspelled, definitely not original|indirect
I want to report a seller selling copies|short
is this even genuine? the box is different from the brand's|indirect,question,multi_sentence
the cologne smells nothing like the real one, fake|indirect
report replica|short
it's a counterfeit, order 55120|entity
bought a 'branded' belt and it's obviously fake|short
authenticity check failed on the bag|short
this seller is selling fakes, take action|angry
the stitching and logo are off, pretty sure it's not real|indirect
fake product complaint|short
got a dupe instead of the real thing|slang
""",
"refund_status": """
refund status|short
where is my refund|short,question
i returned the lamp 10 days ago, where's my money|entity,indirect
refund for order #SH-30019|entity
cancelled my order yesterday, when will the money come back|entity,question
refund not received yet|short
how long do refunds take|question
refud pending|typo,short
Hi, my return was picked up on 2 Sept. Could you check when the refund will be credited?|polite,multi_sentence,entity
it's been a month and no refund, this is ridiculous|angry,entity
has my refund been processed|question
refund of 1,299 still not in my account|entity
the seller accepted my return but refund hasn't started|indirect
money back when?|slang,short
refund went to wallet or bank?|question
my bank doesn't show the refund you said was sent|indirect
update on refund please, Karan Joshi|polite,entity
still no refund for the watch i sent back|indirect
refund status for return RT-5521|entity
why is my refund taking forever|angry,question
you said 5-7 days, it's day 12|indirect,entity
is my refund stuck|question
check refund pls|slang,short
money not credited after cancellation|short
when do i get my money for the returned shoes|question
""",
"login_issue": """
can't log in|short
not getting the OTP|short
forgot my password|short
my account is locked|short
login keeps failing|short
reset password link not coming to my email|indirect
the app says invalid credentials but my password is correct|indirect
otp not recieved on 98200 11223|typo,entity
Hi, I'm unable to sign in to my Shelfy account. Can you help?|polite,multi_sentence
i changed my phone and cant access my account now|indirect
sign in not working!!!|angry
logn problem|typo,short
how do i recover my account, email is priya.s@mail.com|entity,question
too many attempts, it blocked me|indirect
google login isnt working on your site|short
i keep getting logged out and cant get back in|indirect
the verification code expired before it came|indirect
cant access account|short
my old email is gone, how do i log in now|question,indirect
password reset please|polite,short
login page just spins forever|indirect
account says it doesn't exist but i've ordered before|indirect
help i'm locked out|short
OTP comes very late, can't login|indirect
unable to login|short
""",
"__none__": """
ghghgh|gibberish
...|gibberish,short
ok|short
hmm|short
hi|short
what's the weather|off_topic
write an essay on climate change|off_topic
how do i bake a cake|off_topic
where is my order|missing_intent
i want to cancel my order|missing_intent
my item arrived broken|missing_intent
how do i become a seller on shelfy|missing_intent
do you have a coupon|missing_intent
change my delivery address|missing_intent
i want to exchange for a different size|missing_intent
asdf jkl|gibberish
lol|short
who invented the internet|off_topic
thanks|short
123|gibberish,short
play a song|off_topic
qqqqq|gibberish
what time does the sun set|off_topic
can i pay cash on delivery|missing_intent
sdfsdf|gibberish
""",
}),
]
