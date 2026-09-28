"""Food delivery & grocery workflows for synth_0_b. Lines are 'text|tag,tag'."""

WORKFLOWS = [
# ---------------------------------------------------------------- restaurant delivery app, mixed, 8 paths
dict(id="synth0b_munchr_food", paths={
    "where_is_my_food": ["where is my food", "Customer asks how long until their food arrives or where the rider is", "order is late"],
    "missing_items": ["something is missing from my order", "Customer received the order but one or more items were not in the bag"],
    "wrong_order": ["got the wrong order", "Customer received a different dish or someone else's order instead of what they ordered"],
    "food_quality": ["food was cold", "Customer complains the food was spilled, stale, undercooked or tasted bad"],
    "cancel_order": ["cancel my order", "Customer wants to cancel a food order they just placed"],
    "refund_status": ["where is my refund", "Customer asks when a refund for an order will be credited"],
    "change_address": ["change delivery address", "Customer wants to update the address or add directions for the rider"],
    "talk_to_human": ["connect me to support", "talk to an agent"],
}, msgs={
"where_is_my_food": """
where is my food|short,question
its been 50 mins, where is my biryani|entity,angry
rider hasnt moved for 15 min|indirect,entity
how long for order #MN-88213|entity,question
food still not here|short
the app says arriving in 5 min for the last 20 min|indirect,entity
wheres my pizza|slang,short
is the delivery guy lost?|indirect,question
Hi, my order was supposed to arrive at 8:30, it's 9 now. Any update?|polite,multi_sentence,entity
eta??|short
order late|short
im starving, when does my burger get here|slang,question
whre is my order|typo,short
the rider said he's coming but that was 25 min ago|indirect,entity
track my food|short
can you check on my order from Burger Barn|entity
still waiting for my dinner, ordered at 7|entity
why is my delivery taking so long|angry,question
has the restaurant even started preparing my food|question
my food is taking forever|angry,slang
how far is the rider|question
delivery partner not picking up calls and food still not here|indirect
Please tell me when my lunch will reach. I have a meeting at 2|polite,multi_sentence,entity
order status|short
is my order out for delivery|question
""",
"missing_items": """
my fries are missing|short
ordered 3 items got only 2|entity
the coke wasn't in the bag|short
missing item in order #MN-4410|entity
no dessert in my order|short
where's the extra cheese dip i paid for|indirect
the garlic bread is missing from my bag|short
you forgot my drink|short
Hi, I received my order but the paneer tikka was not included.|polite,multi_sentence
only one burger in the bag, i ordered two|entity
misssing item|typo,short
half my order is missing!!|angry
the side salad never came|indirect
got the curry but the rice is missing|short
item missing, charged for it though|short
i paid for 4 rotis and got 2|entity
the sauce packets and the wings are missing|short
bag was sealed but the brownie isn't there|indirect
my kid's meal wasn't in the order|short
order came incomplete|short
the drinks were missing again, second time this week|angry,entity
one pizza short in my order of 3|entity
you left out the naan|slang
received everything except the soup|indirect
missing: 1 x chicken wrap, order 50231|entity
""",
"wrong_order": """
got the wrong order|short
this isn't my food, it's someone else's order|short
i ordered veg and got chicken|short
received a completely different dish|short
the bag has another customer's name on it, Rahul, not me|entity
wrong food delivered order #MN-7712|entity
i asked for a margherita and they sent pepperoni|short
wrng order|typo,short
Hi, I received a sushi platter but I ordered ramen.|polite,multi_sentence
you sent me the wrong restaurant's food|indirect
this is not what i ordered at all!!|angry
got a large coffee instead of a smoothie|short
the whole order is wrong|short
i'm vegetarian and you delivered mutton, disgusting|angry
the receipt on the bag shows order 99012, mine is 99015|entity,indirect
delivered someone else's parcel|short
instead of the paneer wrap i got a fish burger|short
wrong items entirely|short
I got a stranger's order|slang
they sent me spicy wings, i ordered honey garlic|short
this is a wrong order, nothing matches|short
ordered from Taco Town, got chinese food|entity
wrong dish sent|short
the pasta is the wrong one, I asked for alfredo|short
not my order|short
""",
"food_quality": """
the food was cold|short
my soup spilled all over the bag|short
the pizza tasted stale|short
chicken was undercooked, still pink inside|short
the burger was soggy and cold|short
found a hair in my food|short
the curry was way too salty, inedible|short
fries were cold and limp|short
Hi, the noodles arrived lukewarm and the container had leaked.|polite,multi_sentence
foood was stale|typo,short
the milkshake leaked everywhere, bag was soaked|short
this biryani smells off, i think it's spoiled|indirect
disgusting quality, the rice was hard|angry
the ice cream came fully melted|short
the bread was burnt|short
my salad leaves were brown and wilted|short
there was plastic in my wrap|short
the fish tasted weird, i feel sick|indirect
cold food again!!!|angry,short
the sauce container broke and it's everywhere|short
the momos were raw in the middle|short
the coffee was cold by the time it arrived|indirect
pizza toppings all slid off and it was squashed|short
the dessert box was crushed and the cake ruined|short
the paneer was rubbery and tasted old|short
""",
"cancel_order": """
cancel my order|short
please cancel, i ordered by mistake|polite
cancel order #MN-2231|entity
i want to cancel, this is taking too long|angry
cancle the pizza order|typo
changed my mind, dont send the food|indirect
can i still cancel? just placed it|question,multi_sentence
cancel it now|short
ordered from the wrong restaurant, cancel|short
Hi, could you cancel my lunch order? My plans changed.|polite,multi_sentence
cancel the order before the restaurant makes it|short
i placed two orders by mistake, cancel one|indirect
how do i cancel an order|question
nah cancel that|slang,short
i dont want the food anymore|indirect
cancel my dinner order, 45 min wait is too much|entity
cancellation please|polite,short
stop my order|short
is there a fee if i cancel now|question
cancel order for Neha, 99887 66554|entity
i have to leave home, cancel the order|indirect
cancel cancel cancel|angry,short
my friend already brought food, please cancel mine|indirect,polite
cancel the burger order placed at 8:05|entity
abort order|slang,short
""",
"refund_status": """
where is my refund|short,question
refund for the cancelled order still not here|short
you said you'd refund the missing fries, where is it|indirect
refund status order #MN-6612|entity
when will i get my money back|question
refund not credited yet, its been 5 days|entity
i got a refund message but nothing in my bank|indirect
refnd pls check|typo,short
Hi, my order was cancelled by the restaurant yesterday. When will the refund reach me?|polite,multi_sentence
still waiting on my 349 refund|entity
refund to wallet or card?|question
how long does a refund take on munchr|question
my refund is stuck on processing|indirect
this is the third time i'm asking about my refund|angry
has my refund been processed|question
money back status|short
you promised a refund for the cold pizza, not received|indirect
refund id RF-7781 status|entity
the app shows refunded but my UPI hasn't got it|indirect
when do i get refunded for the cancelled order|question
refund??|short
got only half the refund amount, where's the rest|indirect
check my refund, account 98111 00022|entity
refund still pending after a week|short
please update me on my refund|polite
""",
"change_address": """
change delivery address|short
i entered the wrong address, it's flat 302 not 203|entity
can the rider come to the back gate instead|question
update address to 14 MG Road|entity
deliver to my office instead of home|short
wrong pin location on the map, please fix|indirect
adress change pls|typo,short
Hi, I moved to the next building, can you update my address for this order?|polite,question
tell the rider to call when he reaches gate 3|entity
can i change the delivery location now that the order is placed|question
my address is missing the tower name, it's Tower B|entity
send it to my friend's place in Koramangala|entity
the landmark is wrong, it's near the petrol pump|short
please change the drop point to the main lobby|polite
i'm not home, deliver to my neighbour at 5C|entity,indirect
edit address|short
the map pin is 2km off, correct it|entity,indirect
add directions: second floor, ring the bell twice|entity
deliver to reception not the flat|short
I gave the old address by mistake|indirect
change address for order #MN-3009|entity
rider please come to the side entrance|short
move my order to my work address|short
update drop location to Sector 21|entity
wrong house number on my order|short
""",
"talk_to_human": """
connect me to support|short
talk to an agent|short
i want to speak to a real person|short
agent pls|short
human|short
this chat is useless, get me a human|angry
please have someone call me on 90000 12345|entity,polite
can someone from support help me|question
live chat with a person please|polite
escalate this to a manager|short
customer care number|short
huamn agent|typo,short
I'd like to speak with someone from your team|polite
real person now|angry,short
stop sending automated replies, i want a person|angry
is there a human available|question
transfer me to support|short
support executive|short
need to talk to someone|short
let me speak to customer service|short
can i get a callback|question
talk to a human about my order issue|short
someone help me please, a real person|polite
agent|short
representative|short
""",
"__none__": """
qwewqeqw|gibberish
asdf|gibberish
...|gibberish,short
ok|short
hmm|short
hi|short
what's the weather today|off_topic
write me a poem|off_topic
how to lose weight fast|off_topic
tell me a joke|off_topic
do you have any coupons|missing_intent
how do i add a tip for the rider|missing_intent
can i schedule an order for tomorrow|missing_intent
i want to register my restaurant on munchr|missing_intent
is the pizza place open now|missing_intent
how do i delete my account|missing_intent
payment failed while ordering|missing_intent
xdxdxd|gibberish
lol|short
thanks|short
who won the football match|off_topic
convert 10 dollars to euros|off_topic
jhdfjh sdf|gibberish
the rider was rude to me|missing_intent
!!!???|gibberish,short
""",
}),

# ---------------------------------------------------------------- online grocery, description-only style
dict(id="synth0b_freshcart_grocery", paths={
    "book_delivery_slot": ["Customer wants to choose or book a delivery time slot for their grocery order"],
    "substitution_complaint": ["Customer is unhappy that an item was replaced with a different brand or product without asking"],
    "product_availability": ["Customer asks whether a product is in stock or when it will be back"],
    "membership_benefits": ["Customer asks about FreshPass membership price, perks or free delivery"],
    "damaged_or_expired": ["Customer received groceries that were damaged, leaking, rotten or past the expiry date"],
    "payment_failed": ["Customer's payment did not go through or they were charged but the order failed"],
    "greeting": ["Customer says hello or greets the assistant"],
}, msgs={
"book_delivery_slot": """
can i get delivery between 6 and 8 pm|entity,question
book a morning slot for tomorrow|entity
what delivery slots are available on saturday|entity,question
i need my groceries before 10am|entity
slot for sunday evening pls|entity,short
no slots showing for today, can you open one|indirect
choose delivery time|short
dilevery slot booking|typo,short
Hi, can I schedule my order for Friday afternoon?|polite,entity,question
earliest slot possible please|polite,short
i'll be home only after 7, deliver then|indirect,entity
can you deliver at 7am before i leave for work|entity,question
all slots are full!! when can i get delivery|angry,question
express slot in the next 2 hours?|entity,question
pick slot for order #FC-1120|entity
set a weekly delivery slot every monday|entity
move my slot to later in the day|short
i want the late night slot|short
is there a slot tomorrow between 12 and 2|entity,question
please book the 4-6 slot|entity,polite
next available delivery time?|question,short
my mom is home till noon, can you come before that|indirect
book slot 25th morning|entity,short
how do i pick a delivery window|question
weekend slot pls|slang,short
""",
"substitution_complaint": """
you replaced my amul butter with some other brand without asking|entity,angry
i ordered skimmed milk and got full cream as a substitute|short
why did you swap my oat milk for almond milk|question
the substitute you sent is not what i want|short
stop substituting items without asking me|angry
ordered 1kg tomatoes, got cherry tomatoes instead as replacement|entity
sustitution not ok|typo,short
Hi, my order had two items replaced with different brands. I didn't approve that.|polite,multi_sentence
got a different shampoo brand, i didn't agree to a replacement|short
my gluten free bread was replaced with regular bread. I'm celiac, I can't eat this!|multi_sentence,angry
the picker swapped my coffee for a cheaper one|short
the replacement item is way more expensive than what i ordered|indirect
i dont want substitutes, why did you send them|question
you sent pepsi instead of coke without calling me|short
the brown eggs were swapped for white, that's not what i chose|short
why do you always substitute my items|angry,question
bad substitution on order #FC-4471|entity
i asked for no substitutions and you still did it|angry,indirect
the organic spinach was replaced with regular spinach|short
i got a 500g pack instead of the 1kg as a substitute|entity
unhappy with the replacement products|short
the app said 'substituted' for my yoghurt, i didn't want that|indirect
you changed my dog food brand, my dog won't eat it|indirect
the replacement for the jam is a flavour i hate|short
substitutes were terrible this time|short
""",
"product_availability": """
is amul butter in stock|entity,question
do you have almond milk|question
when will the oat milk be back in stock|question
do you sell fresh basil|question
avocados available today?|short,question
nutella is out of stock since a week, when is it coming back|entity,question
Hi, do you stock gluten free pasta?|polite,question
is the 5kg wheat flour pack available|entity,question
do u have greek yogurt|slang,question
availablity of cold brew coffee?|typo,short
i can't find tofu in the app, do you carry it|indirect,question
will you get more of the organic eggs soon|question
is quinoa available in Bangalore|entity,question
the kiwi is showing sold out, restock when|indirect,question
does freshcart sell pet food|question
do you have sugar free ice cream|question
i need 10 packs of paneer for a party, do you have that many|entity,question
any stock of the imported cheddar?|question
when do you restock mangoes|question
is diet coke available near me|question
Do you carry baby formula?|question
cant see coconut water anywhere, is it out|indirect,question
tell me when olive oil is back|indirect
have you got fresh salmon today|question
is the 2L milk pack back yet|entity,question
""",
"membership_benefits": """
how much is freshpass|question
what do i get with the membership|question
does freshpass include free delivery|question
is the membership worth it|question
freshpass benefits?|short,question
how much can i save with freshpass|question
membersip price|typo,short
Hi, can you tell me the perks of the FreshPass plan?|polite,question
is there a monthly or yearly membership|question
do members get extra discounts|question
free delivery with membership has a minimum order?|question
how do i join freshpass|question
what's the difference between freshpass and freshpass plus|question
i'm a member but still paid a delivery fee, why|indirect,question
does the membership cover express delivery|question
trial period for freshpass?|short,question
can i share my membership with family|question
freshpass cost for 3 months|entity
are there member only deals|question
tell me about your membership program|short
is my freshpass active? i'm on 98765 43210|entity,question,multi_sentence
what perks do gold members get|question
does freshpass give cashback|question
sign me up for the membership|short
membership details pls|slang,short
""",
"damaged_or_expired": """
the milk packet was leaking|short
eggs came cracked|short
the bread is past expiry date|short
bananas were rotten|short
received expired yoghurt, date was 3 days ago|entity
the tomatoes are squashed and mushy|short
chips packet torn open|short
oil bottle leaked all over the bag|short
Hi, the paneer I received smells sour and expires today.|polite,multi_sentence
exipred product delivered|typo,short
mouldy bread!!! disgusting|angry,short
the frozen peas arrived thawed and soggy|short
half the eggs in the tray are broken|short
apples have bruises and soft spots everywhere|short
the juice carton is dented and leaking|short
the chicken was warm and smelled off|indirect
my rice bag was torn and rice spilled everywhere|short
cheese is expired by a week, order #FC-2231|entity
the ice cream melted and refroze, it's all icy|indirect
got a damaged tin of beans, huge dent|short
the strawberries were covered in mould|short
the flour had bugs in it|short
why do you send expired stuff!!|angry
spinach was yellow and slimy|short
the biscuits were crushed into powder|short
""",
"payment_failed": """
payment failed|short
money deducted but order failed|short
my card got declined|short
upi payment pending for 20 min|entity
transaction failed twice|entity
charged 1,240 but no order in the app|entity,indirect
paymnt error|typo,short
Hi, my payment didn't go through, but the amount was debited. Please check.|polite,multi_sentence
checkout keeps failing at payment|short
why is my payment not working|angry,question
wallet payment error|short
double charged for order #FC-8812|entity
netbanking timeout and money gone|indirect
cash on delivery greyed out and my card keeps failing|indirect
my payment is stuck|short
paid but it says payment unsuccessful|indirect
got a payment failed message but bank says success|indirect
card payment keeps bouncing back|slang
You took my money and my order got cancelled due to payment failure!|angry
can't pay, the page errors out|short
txn ID 7788123 failed but debited|entity
payment gateway is broken|angry,short
tried 3 cards none work|angry,entity
Apple Pay not going through|entity
order failed after payment|short
""",
"greeting": """
hi|short
hello|short
hey|short
hi freshcart|short
good morning|polite,short
hii|slang,short
heyyy|slang,short
hello there|short
good evening|polite,short
hi, how are you|polite
hellooo|slang,short
hey team|short
morning!|short
hiya|slang,short
helo|typo,short
good afternoon|polite,short
hi it's Sunita|entity,short
hey hey|short
hello :)|short
yo|slang,short
hey there|short
greetings|polite,short
hullo|typo,short
hello, anyone?|short
hi hi|short
""",
"__none__": """
jhkjhk|gibberish
...|gibberish
ok|short
hmm|short
thanks|short
bye|short
what's the weather|off_topic
write me a story|off_topic
give me a recipe for pancakes|off_topic
where is my order|missing_intent
i want to cancel my order|missing_intent
where is my refund|missing_intent
change my delivery address|missing_intent
can i talk to an agent|missing_intent
apply coupon code|missing_intent
asdfghjkl|gibberish
??|gibberish,short
who is the president of usa|off_topic
calculate 15% of 200|off_topic
i want to give feedback about the delivery guy|missing_intent
wewewe|gibberish
lol|short
play music|off_topic
i want to work as a delivery partner|missing_intent
the bill has an extra charge i don't understand|missing_intent
""",
}),

# ---------------------------------------------------------------- tiffin meal subscription, short utterances
dict(id="synth0b_tiffin_daily", paths={
    "skip_a_day": ["skip tomorrow's meal", "no lunch on friday", "skip one day", "dont send dinner tonight", "cancel just tomorrow's tiffin", "i'm out tomorrow, skip it"],
    "pause_subscription": ["pause my plan", "hold my subscription for 2 weeks", "going on vacation, pause meals", "stop deliveries till I'm back", "freeze my tiffin plan"],
    "change_meal_plan": ["switch to veg plan", "change to dinner only", "upgrade my plan", "move to the keto menu", "change my meal plan"],
    "dietary_info": ["is the food jain friendly", "calories in today's meal", "do you use peanuts", "is it gluten free", "how much oil do you use"],
    "thanks_goodbye": ["thanks", "bye", "thank you", "ok thanks", "that's all"],
}, msgs={
"skip_a_day": """
skip tomorrow's lunch|entity
no dinner tonight please|polite
i won't be home on friday, skip that day|entity,indirect
dont send the tiffin on the 14th|entity
skip monday|entity,short
cancel only tomorrow's meal|short
out for a work lunch tomorrow, skip it|indirect
skp tomorow|typo,short
Hi, please don't deliver my lunch on Wednesday. Thanks|polite,multi_sentence,entity
just skip today, i'm eating out|indirect
skip lunch on 3 Oct|entity
no need to send food tomorrow|short
can i skip saturday's dinner|question,entity
not hungry today, skip|slang,short
skip the next meal only|short
i have a party tonight, no dinner needed|indirect
skip 1 day pls|short
don't send tomorrow, i'll be at my sister's|indirect
skip thursday dinner for Anil, 98200 33445|entity
we're fasting tomorrow, skip both meals|indirect
tomorrow off please|short
i forgot to skip today, can you still stop it|question
skip lunch just this once|short
hold tomorrow's delivery only|short
skip day after tomorrow|entity,short
""",
"pause_subscription": """
pause my plan|short
going on vacation for 2 weeks, pause meals|entity
hold my subscription till the 30th|entity
stop deliveries until i get back from my trip|indirect
freeze my tiffin plan for a month|entity
i'm travelling from 5th to 20th, pause everything|entity
pause subscripton|typo,short
Hi, I'll be away for three weeks. Could you pause my plan until then?|polite,multi_sentence,entity
put my meals on hold indefinitely, i'll tell you when to resume|indirect
pause for the whole of december|entity
i'm moving cities for a while, pause my tiffin|indirect
can i pause and resume later?|question
stop sending food for the next 10 days|entity
pause plan from next monday|entity
in hospital, pause meals for a while|indirect
freeze subscription|short
pause my meals, not cancel|short
on leave next week, hold all deliveries|entity,indirect
pls pause till further notice|slang,polite
pause meals for Kavita, 99001 22334|entity
we'll be out of town the whole month, hold the plan|indirect
how do i pause my subscription|question
put everything on hold for 15 days|entity
pause from 1st to 15th|entity,short
i need a break from the plan for a couple of weeks|indirect
""",
"change_meal_plan": """
switch me to the veg plan|short
change to dinner only|short
upgrade to the premium plan|short
move me to the keto menu|short
i want lunch and dinner instead of just lunch|short
downgrade my plan to 5 days a week|entity
chnage plan to high protein|typo
Hi, can I switch from the non-veg to the vegetarian plan from next week?|polite,question,entity
add breakfast to my subscription|short
i'm on a diet now, put me on the low carb plan|indirect
change portion size to large|short
switch to the jain menu|short
can i go from monthly to weekly plan|question
make it 3 meals a day|short
i want the diabetic friendly plan|short
change my plan to weekends only|short
switch my daughter's plan to the kids menu|short
remove dinner from my plan, lunch only|short
upgrade me|short
can i change to the south indian menu|question
switch plan for account TD-5512 to vegan|entity
move me to the family pack, need bigger portions|short
change plan pls|short
i'm tired of the same food, switch me to the international menu|indirect
plan change to 20 meals a month|entity
""",
"dietary_info": """
is the food jain friendly|question
how many calories in today's lunch|question
do you use peanuts in the curry|question
is the paneer made with fresh milk|question
is your food gluten free|question
how much oil do you use|question
is the lentil curry cooked in butter|question
ingrdients in tomorrow's menu?|typo,short,question
Hi, my son has a nut allergy. Is the kids menu safe for him?|polite,multi_sentence,question
protein per meal?|short,question
do you use onion and garlic|question
is the chicken halal|question
what oil do you cook with|question
are the rotis made of whole wheat|question
is there msg in the food|question
how much sugar is in the dessert|question
does the keto meal have any rice|question
is the food suitable for diabetics|question
do you use dairy in the vegan box|question
salt level low? my dad has BP|multi_sentence,question
is it cooked fresh every day|question
any egg in the cakes|question
nutrition info for the high protein plan|short
is the fish boneless|question
what's in today's dinner|question
""",
"thanks_goodbye": """
thanks|short
bye|short
thank you|polite,short
ok thanks|short
that's all|short
thx|slang,short
thank you so much!|polite,short
bye bye|short
cheers|slang,short
great, thanks|short
ty|slang,short
thanks a lot|polite,short
that's everything, bye|short
appreciate it|polite,short
thnx|typo,short
perfect thanks|short
cool, bye|slang,short
thank u so much|polite,short
alright thanks|short
see you|short
thanks for the quick help|polite
okay bye|short
tysm|slang,short
nothing more, thank you|polite,short
good night, thanks|polite,short
""",
"__none__": """
qwqwqw|gibberish
.....|gibberish,short
hmm|short
hi|short
hello|short
what's the weather in Pune|off_topic,entity
write me a haiku|off_topic
who is the richest man in the world|off_topic
where is my tiffin, it's late|missing_intent
the food was cold today|missing_intent
i want to cancel my subscription completely|missing_intent
how do i pay my monthly bill|missing_intent
change my delivery address|missing_intent
can i talk to the chef|missing_intent
refund for a missed meal|missing_intent
sdfsdf|gibberish
lol|short
tell me a joke|off_topic
convert 5 miles to km|off_topic
aaaaa|gibberish
do you have a referral code|missing_intent
the delivery guy was late again|missing_intent
fkfkfk|gibberish
??|gibberish,short
play some music|off_topic
""",
}),

# ---------------------------------------------------------------- quick commerce, short utterances, 6 paths
dict(id="synth0b_quickbasket", paths={
    "order_eta": ["where is my order", "how long will it take", "order late", "eta please", "when will it arrive", "rider location"],
    "add_item": ["add milk to my order", "can i add something", "forgot to add eggs", "add one more item", "include bread in my order"],
    "tip_rider": ["tip the rider", "add a tip", "how do i tip the delivery guy", "give 20 as tip", "change tip amount"],
    "rider_complaint": ["rider was rude", "delivery guy misbehaved", "complain about the delivery person", "rider asked for extra money", "rider didn't come to my door"],
    "apply_coupon": ["apply coupon", "promo code not working", "any discount code", "use my voucher", "coupon for first order"],
    "cancel_order": ["cancel my order", "cancel order", "don't want it anymore", "cancel before it ships", "stop my order"],
}, msgs={
"order_eta": """
where is my order|short,question
its been 20 min, the app promised 10|angry,entity
rider location?|short
eta pls|slang,short
how long till my groceries arrive|question
order #QB-7781 still not here|entity
10 minute delivery my foot, where is it|angry,slang
whre is the rider|typo,short
Hi, can you tell me how far my order is?|polite,question
the map shows the rider standing still|indirect
is my order packed yet|question
still waiting for my milk|indirect
order late|short
when will it arrive, i need the eggs for breakfast|question
my order says 'on the way' for 15 minutes|indirect,entity
has it been picked up from the store|question
arriving soon?|short,question
delivery status for 98200 44556|entity
been waiting half an hour now|angry,indirect,entity
why is this taking so long|angry,question
the ETA keeps increasing|indirect
track order|short
is the rider nearby|question
my snacks order is delayed|short
how many more minutes|question
""",
"add_item": """
add milk to my order|short
can i add something to the order i just placed|question
forgot eggs, add pls|slang
add one more bread|short
include 2 packets of chips|entity
add a coke to order #QB-2201|entity
ad item to order|typo,short
Hi, is it possible to add bananas to my current order?|polite,question
oh no i missed the butter, can you add it|indirect
put in some ice cream too|short
add 1kg onions|entity
can the rider bring detergent as well|question
i need to add another item before it leaves|short
add more to my cart after ordering?|question
also add toothpaste|short
add diapers to the same order|short
can i add items without paying delivery again|question
add 3 lemons|entity,short
forgot to order the curd, add it please|polite
throw in a pack of batteries|slang
add item|short
add yoghurt and honey to my order|short
my wife wants chocolate too, add one|indirect
put a water bottle in the same order|short
can i add a charger cable to my grocery order|question
""",
"tip_rider": """
tip the rider|short
add a tip for the delivery guy|short
how do i tip|question
give 30 as tip|entity
the rider was great, want to tip him|indirect
change tip amount to 50|entity
tpi rider|typo,short
Hi, I'd like to add a tip for my delivery partner. How?|polite,multi_sentence
can i tip in cash|question
remove the tip i added|short
tip 20 for order #QB-6612|entity
rider came in the rain, let me tip extra|indirect
does the rider get the full tip|question
i accidentally tipped 100, change to 10|entity
where is the tip option|question
add tip after delivery?|question
give the delivery boy something extra|indirect
tip rider Ramesh 25|entity
i want to tip but the button is missing|indirect
tip pls|short
default tip setting|short
how much should i tip|question
tip for fast delivery|short
he was so polite, adding a tip|indirect
tip the delivery person 40 please|entity,polite
""",
"rider_complaint": """
rider was rude|short
the delivery guy shouted at me|angry
rider made me come down to the gate even though i paid for door delivery|indirect
delivery person was smoking when he came|short
the rider demanded extra cash|short
complaint about the delivery boy, he was very rude|angry
ridr misbehaved|typo,short
Hi, I want to report the delivery executive. He was abusive on the phone.|polite,multi_sentence
the rider threw the bag at my door|angry
he didn't even come up, then argued with me on call|indirect,angry
your delivery guy was drunk|short
rider parked on my car and was rude when asked|short
delivery person kept calling me names|angry
rider refused to climb the stairs|indirect
i want to complain about rider Suresh from order #QB-5512|entity
the rider was flirting with my sister, not okay|angry
he wasn't wearing a mask and was coughing all over the bag|indirect
rider behaviour was terrible today|short
the delivery man took the tip and then cursed at me|angry
rider was really unprofessional|short
i felt unsafe with the delivery person|indirect
the rider was on his phone while riding and almost hit my kid|indirect
bad experience with the rider|short
report rider|short
the delivery guy was very rude and asked for my number|angry
""",
"apply_coupon": """
apply coupon|short
promo code not working|short
any discount codes today|question
use my voucher QUICK50|entity
coupon for first order?|question
code SAVE20 says invalid|entity
cupon|typo,short
Hi, how do I apply a promo code before checkout?|polite,question
free delivery coupon please|polite
i have a referral code, where to enter|question
forgot to apply the coupon, can you add it now|indirect
code not working!!!|angry
is there any offer on fruits|question
the 100 off coupon isn't applying|entity
minimum order for coupon?|question
cashback code for card payments|short
can i use two coupons|question
coupon expired, any other code|question
new user discount code|short
my promo from the email didn't work|indirect
apply BIGSAVE on my cart|entity
discount code pls|slang,short
why doesn't the coupon work on dairy|question
voucher code|short
the first order code gave me nothing|indirect
""",
"cancel_order": """
cancel my order|short
cancel order #QB-3310|entity
i dont want it anymore|indirect
cancel before the rider picks it up|short
ordered by mistake, cancel|short
cnacel order|typo,short
Hi, please cancel my order, I placed it twice.|polite,multi_sentence
cancel it, too late now|angry
how do i cancel|question
stop my order please|polite
cancel, i found it at the shop downstairs|indirect
can i still cancel?|question,short
cancel the snacks order|short
just cancel it|short
i have to leave, cancel the delivery|indirect
cancel order for 99000 77665|entity
is there a charge for cancelling|question
changed my mind, no order|slang
cancel pls|short
cancel my grocery order from 7:40|entity
cancel right now!!|angry,short
put the wrong address, just cancel it|indirect
please cancel the whole order|polite
nah cancel|slang,short
cancel my last order|short
""",
"__none__": """
qweqwe|gibberish
...|gibberish,short
ok|short
hmm|short
hi|short
thanks|short
what's the weather|off_topic
write me a song|off_topic
what's 12 times 12|off_topic
tell me about black holes|off_topic
i got the wrong item|missing_intent
my eggs were broken|missing_intent
where is my refund|missing_intent
change my address|missing_intent
do you deliver in Noida|missing_intent,entity
talk to agent|missing_intent
payment failed|missing_intent
remove an item from my order|missing_intent
zzz|gibberish
lol|short
jkjkjk|gibberish
who won the election|off_topic
recommend a netflix show|off_topic
asdjkl|gibberish
the app keeps crashing|missing_intent
""",
}),

# ---------------------------------------------------------------- restaurant reservations, description style, 3 paths
dict(id="synth0b_tabletap_restaurant", paths={
    "book_table": ["Customer wants to reserve a table at the restaurant for a date, time and party size"],
    "cancel_reservation": ["Customer wants to cancel or call off an existing table booking"],
    "opening_hours": ["Customer asks when the restaurant opens or closes, or if it is open on a given day"],
}, msgs={
"book_table": """
table for 4 tonight at 8|entity
can i book a table for saturday lunch|entity,question
reserve for 2 at 7:30 pm tomorrow|entity
need a table for 10 people for a birthday on 5th Nov|entity
booking for two please|polite,short
do you have a table free right now for 3|entity,question
reserv table|typo,short
Hi, I'd like to make a reservation for Friday evening, 6 people.|polite,entity
book a window table for our anniversary|short
table for one at 1pm|entity
can we get a table outside on sunday|entity,question
i want to reserve for 8 people this weekend|entity
any availability for dinner tonight? party of 5|entity,question,multi_sentence
book me in for brunch sunday 11am|entity
reservation under the name Mehta for 4 at 9|entity
is it possible to book the private room for 15|entity,question
table for 2 pls|short
we're coming with a baby, need a table with a high chair tomorrow night|entity,indirect
reserve dinner for my team of 12 on the 18th|entity
can i book for new year's eve|question,entity
couple of us coming at 8, can you hold a table|slang,entity
i'd like to book a table|polite
table tomorrow lunch for 3|entity,short
book table 7pm|entity,short
get me a spot for 4 friends at 9:30 tonight|slang,entity
""",
"cancel_reservation": """
cancel my reservation|short
cancel the table for 4 tonight|entity
we can't make it tomorrow, cancel our booking|indirect,entity
please cancel booking ref TT-4471|entity,polite
cancl booking|typo,short
Hi, I need to cancel my reservation for Saturday. Sorry!|polite,multi_sentence,entity
call off the dinner booking|short
we're not coming, cancel it|indirect
cancel reservation under Sharma|entity
something came up, cancel the 8pm table|indirect,entity
how do i cancel a booking|question
cancel the birthday reservation for 10|entity
our plans fell through, please drop the table|indirect
remove my booking for friday|entity
i want to cancel the table i booked yesterday|entity
is there a fee to cancel my reservation|question
cancel the table, phone 98111 44556|entity
no longer need the table|indirect
cancel both my bookings this week|short
won't be coming for brunch, cancel|indirect
please scrap the reservation|polite,slang
cancel booking|short
my friend is sick so cancel our lunch table|indirect
cancel tonight's reservation|short
can i cancel the table for 6 on the 12th|entity,question
""",
"opening_hours": """
what time do you open|question
are you open on sunday|question,entity
closing time today?|short,question
open now?|short,question
what are your hours|question
are you open on christmas day|entity,question
till what time is the kitchen open|question
opning hours|typo,short
Hi, what time do you close on Fridays?|polite,question,entity
are you open for breakfast|question
do you open on mondays|question,entity
last order time?|short,question
what time does lunch service start|question
is the restaurant open late on weekends|question
are you open on public holidays|question
open tomorrow morning?|short,question
hours please|polite,short
when do u guys shut|slang,question
are you closed today|question
what's the latest i can walk in for dinner|question
timings|short
open at 7am?|entity,short,question
we're nearby. are you open right now?|multi_sentence,question
what time do you open on new year's day|entity,question
do you stay open past midnight|question
""",
"__none__": """
asdfgh|gibberish
...|gibberish,short
ok|short
hmm|short
hi|short
thanks|short
what's the weather tonight|off_topic
write a poem about pizza|off_topic
how tall is mount everest|off_topic
do you have vegan options on the menu|missing_intent
can i order takeaway|missing_intent
where are you located|missing_intent
do you have parking|missing_intent
is there a dress code|missing_intent
can i see the menu|missing_intent
how much is a meal for two|missing_intent
my food at your restaurant was cold|missing_intent
qqwwee|gibberish
lol|short
tell me a joke|off_topic
who wrote hamlet|off_topic
hjhjhj|gibberish
i left my umbrella at your restaurant yesterday|missing_intent
are you hiring waiters|missing_intent
??|gibberish,short
""",
}),
]
