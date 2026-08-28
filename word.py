"""
Wordle Word Filter
===================

Tkinter GUI that filters a 5-letter word list down to the words that
are still possible, based on the clues Wordle gives you:

    - grey / absent    : letter is not in the word at all
    - yellow / present : letter is in the word, but not at that position
    - green / fixed    : letter is confirmed at that exact position

Clue handling
-------------
A "grey" letter only excludes a word if that letter isn't *also*
marked yellow or green somewhere else. This covers repeated-letter
cases correctly (e.g. the answer has one "e", you guessed two: one
came back green, the other grey).

Theming
-------
Same color-token approach as the DMX Derby Controller project
(COLOR_BG / COLOR_BG_LIGHT / COLOR_FG / COLOR / COLOR_DARK /
COLOR_STATUS_TEXT), bundled into named themes and switchable at
runtime from the dropdown instead of being commented in/out.
"""

import re
import tkinter as tk
from tkinter import ttk, scrolledtext

#from wordlist import WORDS

WORDS = "aback,abase,abate,abbey,abbot,abhor,abide,abled,abode,abort,about,above,abuse,abyss,acorn,acrid,actor,acute,adage,adapt,adept,admin,admit,adobe,adopt,adore,adorn,adult,affix,afire,afoot,afoul,after,again,agape,agate,agent,agile,aging,aglow,agony,agree,ahead,aider,aisle,alarm,album,alert,algae,alibi,alien,align,alike,alive,allay,alley,allot,allow,alloy,aloft,alone,along,aloof,aloud,alpha,altar,alter,amass,amaze,amber,amble,amend,amiss,amity,among,ample,amply,amuse,angel,anger,angle,angry,angst,anime,ankle,annex,annoy,annul,anode,antic,anvil,aorta,apart,aphid,aping,apnea,apple,apply,apron,aptly,arbor,ardor,arena,argue,arise,armor,aroma,arose,array,arrow,arson,artsy,ascot,ashen,aside,askew,assay,asset,atoll,atone,attic,audio,audit,augur,aunty,avail,avert,avian,avoid,await,awake,award,aware,awash,awful,awoke,axial,axiom,axion,azure,bacon,badge,badly,bagel,baggy,baker,baler,balmy,banal,banjo,barge,baron,basal,basic,basil,basin,basis,baste,batch,bathe,baton,batty,bawdy,bayou,beach,beady,beard,beast,beech,beefy,befit,began,begat,beget,begin,begun,being,belch,belie,belle,belly,below,bench,beret,berry,berth,beset,betel,bevel,bezel,bible,bicep,biddy,bigot,bilge,billy,binge,bingo,biome,birch,birth,bison,bitty,black,blade,blame,bland,blank,blare,blast,blaze,bleak,bleat,bleed,bleep,blend,bless,blimp,blind,blink,bliss,blitz,bloat,block,bloke,blond,blood,bloom,blown,bluer,bluff,blunt,blurb,blurt,blush,board,boast,bobby,boney,bongo,bonus,booby,boost,booth,booty,booze,boozy,borax,borne,bosom,bossy,botch,bough,boule,bound,bowel,boxer,brace,braid,brain,brake,brand,brash,brass,brave,bravo,brawl,brawn,bread,break,breed,briar,bribe,brick,bride,brief,brine,bring,brink,briny,brisk,broad,broil,broke,brood,brook,broom,broth,brown,brunt,brush,brute,buddy,budge,buggy,bugle,build,built,bulge,bulky,bully,bunch,bunny,burly,burnt,burst,bused,bushy,butch,butte,buxom,buyer,bylaw,cabal,cabby,cabin,cable,cacao,cache,cacti,caddy,cadet,cagey,cairn,camel,cameo,canal,candy,canny,canoe,canon,caper,caput,carat,cargo,carol,carry,carve,caste,catch,cater,catty,caulk,cause,cavil,cease,cedar,cello,chafe,chaff,chain,chair,chalk,champ,chant,chaos,chard,charm,chart,chase,chasm,cheap,cheat,check,cheek,cheer,chess,chest,chick,chide,chief,child,chili,chill,chime,china,chirp,chock,choir,choke,chord,chore,chose,chuck,chump,chunk,churn,chute,cider,cigar,cinch,circa,civic,civil,clack,claim,clamp,clang,clank,clash,clasp,class,clean,clear,cleat,cleft,clerk,click,cliff,climb,cling,clink,cloak,clock,clone,close,cloth,cloud,clout,clove,clown,cluck,clued,clump,clung,coach,coast,cobra,cocoa,colon,color,comet,comfy,comic,comma,conch,condo,conic,copse,coral,corer,corny,couch,cough,could,count,coupe,court,coven,cover,covet,covey,cower,coyly,crack,craft,cramp,crane,crank,crash,crass,crate,crave,crawl,craze,crazy,creak,cream,credo,creed,creek,creep,creme,crepe,crept,cress,crest,crick,cried,crier,crime,crimp,crisp,croak,crock,crone,crony,crook,cross,croup,crowd,crown,crude,cruel,crumb,crump,crush,crust,crypt,cubic,cumin,curio,curly,curry,curse,curve,curvy,cutie,cyber,cycle,cynic,daddy,daily,dairy,daisy,dally,dance,dandy,datum,daunt,dealt,death,debar,debit,debug,debut,decal,decay,decor,decoy,decry,defer,deign,deity,delay,delta,delve,demon,demur,denim,dense,depot,depth,derby,deter,detox,deuce,devil,diary,dicey,digit,dilly,dimly,diner,dingo,dingy,diode,dirge,dirty,disco,ditch,ditto,ditty,diver,dizzy,dodge,dodgy,dogma,doing,dolly,donor,donut,dopey,doubt,dough,dowdy,dowel,downy,dowry,dozen,draft,drain,drake,drama,drank,drape,drawl,drawn,dread,dream,dress,dried,drier,drift,drill,drink,drive,droit,droll,drone,drool,droop,dross,drove,drown,druid,drunk,dryer,dryly,duchy,dully,dummy,dumpy,dunce,dusky,dusty,dutch,duvet,dwarf,dwell,dwelt,dying,eager,eagle,early,earth,easel,eaten,eater,ebony,eclat,edict,edify,eerie,egret,eight,eject,eking,elate,elbow,elder,elect,elegy,elfin,elide,elite,elope,elude,email,embed,ember,emcee,empty,enact,endow,enema,enemy,enjoy,ennui,ensue,enter,entry,envoy,epoch,epoxy,equal,equip,erase,erect,erode,error,erupt,essay,ester,ether,ethic,ethos,etude,evade,event,every,evict,evoke,exact,exalt,excel,exert,exile,exist,expel,extol,extra,exult,eying,fable,facet,faint,fairy,faith,FALSE,fancy,fanny,farce,fatal,fatty,fault,fauna,favor,feast,fecal,feign,fella,felon,femme,femur,fence,feral,ferry,fetal,fetch,fetid,fetus,fever,fewer,fiber,ficus,field,fiend,fiery,fifth,fifty,fight,filer,filet,filly,filmy,filth,final,finch,finer,first,fishy,fixer,fizzy,fjord,flack,flail,flair,flake,flaky,flame,flank,flare,flash,flask,fleck,fleet,flesh,flick,flier,fling,flint,flirt,float,flock,flood,floor,flora,floss,flour,flout,flown,fluff,fluid,fluke,flume,flung,flunk,flush,flute,flyer,foamy,focal,focus,foggy,foist,folio,folly,foray,force,forge,forgo,forte,forth,forty,forum,found,foyer,frail,frame,frank,fraud,freak,freed,freer,fresh,friar,fried,frill,frisk,fritz,frock,frond,front,frost,froth,frown,froze,fruit,fudge,fugue,fully,fungi,funky,funny,furor,furry,fussy,fuzzy,gaffe,gaily,gamer,gamma,gamut,gassy,gaudy,gauge,gaunt,gauze,gavel,gawky,gayer,gayly,gazer,gecko,geeky,geese,genie,genre,ghost,ghoul,giant,giddy,gipsy,girly,girth,given,giver,glade,gland,glare,glass,glaze,gleam,glean,glide,glint,gloat,globe,gloom,glory,gloss,glove,glyph,gnash,gnome,godly,going,golem,golly,gonad,goner,goody,gooey,goofy,goose,gorge,gouge,gourd,grace,grade,graft,grail,grain,grand,grant,grape,graph,grasp,grass,grate,grave,gravy,graze,great,greed,green,greet,grief,grill,grime,grimy,grind,gripe,groan,groin,groom,grope,gross,group,grout,grove,growl,grown,gruel,gruff,grunt,guard,guava,guess,guest,guide,guild,guile,guilt,guise,gulch,gully,gumbo,gummy,guppy,gusto,gusty,gypsy,habit,hairy,halve,handy,happy,hardy,harem,harpy,harry,harsh,haste,hasty,hatch,hater,haunt,haute,haven,havoc,hazel,heady,heard,heart,heath,heave,heavy,hedge,hefty,heist,helix,hello,hence,heron,hilly,hinge,hippo,hippy,hitch,hoard,hobby,hoist,holly,homer,honey,honor,horde,horny,horse,hotel,hotly,hound,house,hovel,hover,howdy,human,humid,humor,humph,humus,hunch,hunky,hurry,husky,hussy,hutch,hydro,hyena,hymen,hyper,icily,icing,ideal,idiom,idiot,idler,idyll,igloo,iliac,image,imbue,impel,imply,inane,inbox,incur,index,inept,inert,infer,ingot,inlay,inlet,inner,input,inter,intro,ionic,irate,irony,islet,issue,itchy,ivory,jaunt,jazzy,jelly,jerky,jetty,jewel,jiffy,joint,joist,joker,jolly,joust,judge,juice,juicy,jumbo,jumpy,junta,junto,juror,kappa,karma,kayak,kebab,khaki,kinky,kiosk,kitty,knack,knave,knead,kneed,kneel,knelt,knife,knock,knoll,known,koala,krill,label,labor,laden,ladle,lager,lance,lanky,lapel,lapse,large,larva,lasso,latch,later,lathe,latte,laugh,layer,leach,leafy,leaky,leant,leapt,learn,lease,leash,least,leave,ledge,leech,leery,lefty,legal,leggy,lemon,lemur,leper,level,lever,libel,liege,light,liken,lilac,limbo,limit,linen,liner,lingo,lipid,lithe,liver,livid,llama,loamy,loath,lobby,local,locus,lodge,lofty,logic,login,loopy,loose,lorry,loser,louse,lousy,lover,lower,lowly,loyal,lucid,lucky,lumen,lumpy,lunar,lunch,lunge,lupus,lurch,lurid,lusty,lying,lymph,lyric,macaw,macho,macro,madam,madly,mafia,magic,magma,maize,major,maker,mambo,mamma,mammy,manga,mange,mango,mangy,mania,manic,manly,manor,maple,march,marry,marsh,mason,masse,match,matey,mauve,maxim,maybe,mayor,mealy,meant,meaty,mecca,medal,media,medic,melee,melon,mercy,merge,merit,merry,metal,meter,metro,micro,midge,midst,might,milky,mimic,mince,miner,minim,minor,minty,minus,mirth,miser,missy,mocha,modal,model,modem,mogul,moist,molar,moldy,money,month,moody,moose,moral,moron,morph,mossy,motel,motif,motor,motto,moult,mound,mount,mourn,mouse,mouth,mover,movie,mower,mucky,mucus,muddy,mulch,mummy,munch,mural,murky,mushy,music,musky,musty,myrrh,nadir,naive,nanny,nasal,nasty,natal,naval,navel,needy,neigh,nerdy,nerve,never,newer,newly,nicer,niche,niece,night,ninja,ninny,ninth,noble,nobly,noise,noisy,nomad,noose,north,nosey,notch,novel,nudge,nurse,nutty,nylon,nymph,oaken,obese,occur,ocean,octal,octet,odder,oddly,offal,offer,often,olden,older,olive,ombre,omega,onion,onset,opera,opine,opium,optic,orbit,order,organ,other,otter,ought,ounce,outdo,outer,outgo,ovary,ovate,overt,ovine,ovoid,owing,owner,oxide,ozone,paddy,pagan,paint,paler,palsy,panel,panic,pansy,papal,paper,parer,parka,parry,parse,party,pasta,paste,pasty,patch,patio,patsy,patty,pause,payee,payer,peace,peach,pearl,pecan,pedal,penal,pence,penne,penny,perch,peril,perky,pesky,pesto,petal,petty,phase,phone,phony,photo,piano,picky,piece,piety,piggy,pilot,pinch,piney,pinky,pinto,piper,pique,pitch,pithy,pivot,pixel,pixie,pizza,place,plaid,plain,plait,plane,plank,plant,plate,plaza,plead,pleat,plied,plier,pluck,plumb,plume,plump,plunk,plush,poesy,point,poise,poker,polar,polka,polyp,pooch,poppy,porch,poser,posit,posse,pouch,pound,pouty,power,prank,prawn,preen,press,price,prick,pride,pried,prime,primo,print,prior,prism,privy,prize,probe,prone,prong,proof,prose,proud,prove,prowl,proxy,prude,prune,psalm,pubic,pudgy,puffy,pulpy,pulse,punch,pupil,puppy,puree,purer,purge,purse,pushy,putty,pygmy,quack,quail,quake,qualm,quark,quart,quash,quasi,queen,queer,quell,query,quest,queue,quick,quiet,quill,quilt,quirk,quite,quota,quote,quoth,rabbi,rabid,racer,radar,radii,radio,rainy,raise,rajah,rally,ralph,ramen,ranch,randy,range,rapid,rarer,raspy,ratio,ratty,raven,rayon,razor,reach,react,ready,realm,rearm,rebar,rebel,rebus,rebut,recap,recur,recut,reedy,refer,refit,regal,rehab,reign,relax,relay,relic,remit,renal,renew,repay,repel,reply,rerun,reset,resin,retch,retro,retry,reuse,revel,revue,rhino,rhyme,rider,ridge,rifle,right,rigid,rigor,rinse,ripen,riper,risen,riser,risky,rival,river,rivet,roach,roast,robin,robot,rocky,rodeo,roger,rogue,roomy,roost,rotor,rouge,rough,round,rouse,route,rover,rowdy,rower,royal,ruddy,ruder,rugby,ruler,rumba,rumor,rupee,rural,rusty,sadly,safer,saint,salad,sally,salon,salsa,salty,salve,salvo,sandy,saner,sappy,sassy,satin,satyr,sauce,saucy,sauna,saute,savor,savoy,savvy,scald,scale,scalp,scaly,scamp,scant,scare,scarf,scary,scene,scent,scion,scoff,scold,scone,scoop,scope,score,scorn,scour,scout,scowl,scram,scrap,scree,screw,scrub,scrum,scuba,sedan,seedy,segue,seize,semen,sense,sepia,serif,serum,serve,setup,seven,sever,sewer,shack,shade,shady,shaft,shake,shaky,shale,shall,shalt,shame,shank,shape,shard,share,shark,sharp,shave,shawl,shear,sheen,sheep,sheer,sheet,sheik,shelf,shell,shied,shift,shine,shiny,shire,shirk,shirt,shoal,shock,shone,shook,shoot,shore,shorn,short,shout,shove,shown,showy,shrew,shrub,shrug,shuck,shunt,shush,shyly,siege,sieve,sight,sigma,silky,silly,since,sinew,singe,siren,sissy,sixth,sixty,skate,skier,skiff,skill,skimp,skirt,skulk,skull,skunk,slack,slain,slang,slant,slash,slate,sleek,sleep,sleet,slept,slice,slick,slide,slime,slimy,sling,slink,sloop,slope,slosh,sloth,slump,slung,slunk,slurp,slush,slyly,smack,small,smart,smash,smear,smell,smelt,smile,smirk,smite,smith,smock,smoke,smoky,smote,snack,snail,snake,snaky,snare,snarl,sneak,sneer,snide,sniff,snipe,snoop,snore,snort,snout,snowy,snuck,snuff,soapy,sober,soggy,solar,solid,solve,sonar,sonic,sooth,sooty,sorry,sound,south,sower,space,spade,spank,spare,spark,spasm,spawn,speak,spear,speck,speed,spell,spelt,spend,spent,sperm,spice,spicy,spied,spiel,spike,spiky,spill,spilt,spine,spiny,spire,spite,splat,split,spoil,spoke,spoof,spook,spool,spoon,spore,sport,spout,spray,spree,sprig,spunk,spurn,spurt,squad,squat,squib,stack,staff,stage,staid,stain,stair,stake,stale,stalk,stall,stamp,stand,stank,stare,stark,start,stash,state,stave,stead,steak,steal,steam,steed,steel,steep,steer,stein,stern,stick,stiff,still,stilt,sting,stink,stint,stock,stoic,stoke,stole,stomp,stone,stony,stood,stool,stoop,store,stork,storm,story,stout,stove,strap,straw,stray,strip,strut,stuck,study,stuff,stump,stung,stunk,stunt,style,suave,sugar,suing,suite,sulky,sully,sumac,sunny,super,surer,surge,surly,sushi,swami,swamp,swarm,swash,swath,swear,sweat,sweep,sweet,swell,swept,swift,swill,swine,swing,swirl,swish,swoon,swoop,sword,swore,sworn,swung,synod,syrup,tabby,table,taboo,tacit,tacky,taffy,taint,taken,taker,tally,talon,tamer,tango,tangy,taper,tapir,tardy,tarot,taste,tasty,tatty,taunt,tawny,teach,teary,tease,teddy,teeth,tempo,tenet,tenor,tense,tenth,tepee,tepid,terra,terse,testy,thank,theft,their,theme,there,these,theta,thick,thief,thigh,thing,think,third,thong,thorn,those,three,threw,throb,throw,thrum,thumb,thump,thyme,tiara,tibia,tidal,tiger,tight,tilde,timer,timid,tipsy,titan,tithe,title,toast,today,toddy,token,tonal,tonga,tonic,tooth,topaz,topic,torch,torso,torus,total,totem,touch,tough,towel,tower,toxic,toxin,trace,track,tract,trade,trail,train,trait,tramp,trash,trawl,tread,treat,trend,triad,trial,tribe,trice,trick,tried,tripe,trite,troll,troop,trope,trout,trove,truce,truck,truer,truly,trump,trunk,truss,trust,truth,tryst,tubal,tuber,tulip,tulle,tumor,tunic,turbo,tutor,twang,tweak,tweed,tweet,twice,twine,twirl,twist,twixt,tying,udder,ulcer,ultra,umbra,uncle,uncut,under,undid,undue,unfed,unfit,unify,union,unite,unity,unlit,unmet,unset,untie,until,unwed,unzip,upper,upset,urban,urine,usage,usher,using,usual,usurp,utile,utter,vague,valet,valid,valor,value,valve,vapid,vapor,vault,vaunt,vegan,venom,venue,verge,verse,verso,verve,vicar,video,vigil,vigor,villa,vinyl,viola,viper,viral,virus,visit,visor,vista,vital,vivid,vixen,vocal,vodka,vogue,voice,voila,vomit,voter,vouch,vowel,vying,wacky,wafer,wager,wagon,waist,waive,waltz,warty,waste,watch,water,waver,waxen,weary,weave,wedge,weedy,weigh,weird,welch,welsh,whack,whale,wharf,wheat,wheel,whelp,where,which,whiff,while,whine,whiny,whirl,whisk,white,whole,whoop,whose,widen,wider,widow,width,wield,wight,willy,wimpy,wince,winch,windy,wiser,wispy,witch,witty,woken,woman,women,woody,wooer,wooly,woozy,wordy,world,worry,worse,worst,worth,would,wound,woven,wrack,wrath,wreak,wreck,wrest,wring,wrist,write,wrong,wrote,wrung,wryly,yacht,yearn,yeast,yield,young,youth,zebra,zesty,zonal".split(",")

WORD_LENGTH = 5

THEMES = {
    "Dark / Purple": dict(
        BG="#1e1e24", BG_LIGHT="#2a2a33", FG="#e0dff0",
        ACCENT="#9b59d9", ACCENT_DARK="#6c3fa0", STATUS_TEXT="#c9a6f5",
    ),
    "Dark / Blue": dict(
        BG="#1e1e24", BG_LIGHT="#2a2a33", FG="#e0dff0",
        ACCENT="#4a90d9", ACCENT_DARK="#2f5f9e", STATUS_TEXT="#a6c9f5",
    ),
    "Black / White": dict(
        BG="#000000", BG_LIGHT="#1a1a1a", FG="#ffffff",
        ACCENT="#ffffff", ACCENT_DARK="#808080", STATUS_TEXT="#d9d9d9",
    ),
}
DEFAULT_THEME = "Dark / Purple"


class WordleFilter:
    """Filters a word list based on Wordle-style clues."""

    def __init__(self, wordlist, word_length=WORD_LENGTH):
        self.word_length = word_length
        self.wordlist = [
            w.strip().lower() for w in wordlist
            if len(w.strip()) == word_length
        ]
        self.reset()

    def reset(self):
        """Clears all clues (the loaded word list itself is kept)."""
        self.absent_letters = set()   # grey: not in the word at all
        self.present_letters = {}     # yellow: letter -> {excluded positions}
        self.fixed_positions = {}     # green: position -> letter

    def add_absent(self, letters):
        self.absent_letters.update(letters)

    def add_present(self, letter, position):
        """`position` is 0-indexed. The letter is known to be in the
        word, just not at this position."""
        self.present_letters.setdefault(letter, set()).add(position)

    def add_fixed(self, position, letter):
        self.fixed_positions[position] = letter

    def _matches(self, word):
        # green: letter must sit exactly here
        for pos, letter in self.fixed_positions.items():
            if pos >= len(word) or word[pos] != letter:
                return False

        # yellow: letter must be in the word, just not at these positions
        for letter, excluded_positions in self.present_letters.items():
            if letter not in word:
                return False
            for pos in excluded_positions:
                if pos < len(word) and word[pos] == letter:
                    return False

        # grey: letter must not appear at all, UNLESS it's also
        # confirmed present elsewhere (duplicate-letter case)
        known_present = set(self.fixed_positions.values()) | set(self.present_letters)
        for letter in self.absent_letters:
            if letter in known_present:
                continue
            if letter in word:
                return False

        return True

    def filter(self):
        return [w for w in self.wordlist if self._matches(w)]


# ------------------------------------------------------------
# Themed popup, same approach as the DMX Derby Controller project
# (nicer than the default tkinter.messagebox, and follows the
# current theme instead of using the OS dialog style)
# ------------------------------------------------------------
class ThemedDialog(tk.Toplevel):
    """Modal popup styled to match the app's current color theme."""

    def __init__(self, parent, title, message, buttons):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=parent.winfo_toplevel()["bg"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None

        ttk.Label(self, text=message, wraplength=280, justify="left").pack(
            padx=20, pady=(20, 10)
        )

        btn_row = ttk.Frame(self)
        btn_row.pack(padx=20, pady=(0, 20))
        for label in buttons:
            ttk.Button(
                btn_row, text=label,
                command=lambda l=label: self._on_button(l),
            ).pack(side="left", padx=5)

        self.bind("<Escape>", lambda e: self._on_button(None))
        self.protocol("WM_DELETE_WINDOW", lambda: self._on_button(None))

        self.update_idletasks()
        self._center_on(parent)
        self.wait_window(self)

    def _center_on(self, parent):
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _on_button(self, label):
        self.result = label
        self.grab_release()
        self.destroy()


def show_error(parent, title, message):
    ThemedDialog(parent, title, message, buttons=["OK"])


class WordleFilterApp:
    """Tkinter UI for the Wordle Word Filter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Word Filter")
        self.root.resizable(False, False)

        self.wf = WordleFilter(WORDS)
        self.theme_name = tk.StringVar(value=DEFAULT_THEME)

        self._build_theme_bar()
        self._build_input_form()
        self._build_result_area()

        self._apply_theme(DEFAULT_THEME)

    # ------------------------------------------------------------
    # Theming
    # ------------------------------------------------------------
    def _apply_theme(self, theme_name):
        c = THEMES[theme_name]
        self.root.configure(bg=c["BG"])

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".", background=c["BG"], foreground=c["FG"], font=("Segoe UI", 9))
        style.configure("TFrame", background=c["BG"])
        style.configure("TLabelframe", background=c["BG"], foreground=c["FG"], bordercolor=c["ACCENT_DARK"])
        style.configure("TLabelframe.Label", background=c["BG"], foreground=c["ACCENT"])
        style.configure("TLabel", background=c["BG"], foreground=c["FG"])

        style.configure("TButton", background=c["BG_LIGHT"], foreground=c["FG"],
                         bordercolor=c["ACCENT_DARK"], focusthickness=1, padding=6)
        style.map("TButton",
                  background=[("active", c["ACCENT_DARK"]), ("pressed", c["ACCENT"])],
                  foreground=[("active", c["FG"])])

        style.configure("TCombobox", fieldbackground=c["BG_LIGHT"], background=c["BG_LIGHT"],
                         foreground=c["FG"], arrowcolor=c["ACCENT"])
        style.map("TCombobox", fieldbackground=[("readonly", c["BG_LIGHT"])])

        style.configure("TEntry", fieldbackground=c["BG_LIGHT"], foreground=c["FG"],
                         insertcolor=c["FG"])

        style.configure("Filter.TButton", background=c["ACCENT_DARK"], foreground=c["FG"])
        style.map("Filter.TButton", background=[("active", c["ACCENT"])])

        style.configure("Count.TLabel", background=c["BG"], foreground=c["STATUS_TEXT"],
                         font=("Segoe UI", 9, "bold"))

        # scrolledtext.ScrolledText is plain tk, not ttk -- style it by hand
        self.text_result.configure(
            bg=c["BG_LIGHT"], fg=c["FG"], insertbackground=c["FG"],
            selectbackground=c["ACCENT_DARK"],
        )

    def _on_theme_change(self, event=None):
        self._apply_theme(self.theme_name.get())

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def _build_theme_bar(self):
        bar = ttk.Frame(self.root, padding=10)
        bar.pack(fill="x")

        ttk.Label(bar, text="Theme:").pack(side="left", padx=(0, 5))
        theme_cb = ttk.Combobox(
            bar, textvariable=self.theme_name, values=list(THEMES),
            state="readonly", width=15,
        )
        theme_cb.pack(side="left")
        theme_cb.bind("<<ComboboxSelected>>", self._on_theme_change)

    def _build_input_form(self):
        form = ttk.LabelFrame(self.root, text="Clues", padding=10)
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Absent letters (grey), e.g. xyz").grid(
            row=0, column=0, sticky="w", padx=5, pady=4)
        self.entry_absent = ttk.Entry(form, width=40)
        self.entry_absent.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form, text="Correct position (green), e.g. 1:c,3:r").grid(
            row=1, column=0, sticky="w", padx=5, pady=4)
        self.entry_fixed = ttk.Entry(form, width=40)
        self.entry_fixed.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form, text="Wrong position (yellow), e.g. 2:a,4:a").grid(
            row=2, column=0, sticky="w", padx=5, pady=4)
        self.entry_present = ttk.Entry(form, width=40)
        self.entry_present.grid(row=2, column=1, padx=5, pady=4)

        btn_row = ttk.Frame(form)
        btn_row.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_row, text="Filter", command=self.run_filter,
                   style="Filter.TButton").pack(side="left", padx=5)
        ttk.Button(btn_row, text="Reset", command=self.reset_form).pack(side="left", padx=5)

    def _build_result_area(self):
        result = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        result.pack(fill="both", expand=True)

        self.count_label = ttk.Label(result, text="0 possible words", style="Count.TLabel")
        self.count_label.pack(anchor="w", pady=(0, 5))

        self.text_result = scrolledtext.ScrolledText(result, width=60, height=20, relief="flat")
        self.text_result.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    # Parsing / validation (fixes silently-ignored bad input)
    # ------------------------------------------------------------
    @staticmethod
    def _parse_letters(raw):
        """Returns the lowercase a-z letters in raw, or raises ValueError."""
        raw = raw.strip().lower()
        if raw and not re.fullmatch(r"[a-z]*", raw):
            raise ValueError(f"'{raw}' should only contain letters a-z.")
        return raw

    def _parse_position_pairs(self, raw, field_name):
        """Parses 'pos:letter,pos:letter,...' into a list of
        (0-indexed position, letter) tuples. `pos` is 1-indexed by the
        user, matching the 1..WORD_LENGTH they see on screen."""
        raw = raw.strip()
        pairs = []
        if not raw:
            return pairs
        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue
            if ":" not in item:
                raise ValueError(f"{field_name}: '{item}' is missing a ':' (expected e.g. '1:c').")
            pos_str, letter = item.split(":", 1)
            letter = letter.strip().lower()
            if not re.fullmatch(r"[a-z]", letter):
                raise ValueError(f"{field_name}: '{item}' -- letter must be a single a-z character.")
            try:
                pos = int(pos_str.strip())
            except ValueError:
                raise ValueError(f"{field_name}: '{item}' -- position must be a number.")
            if not (1 <= pos <= self.wf.word_length):
                raise ValueError(
                    f"{field_name}: position {pos} is out of range "
                    f"(1-{self.wf.word_length})."
                )
            pairs.append((pos - 1, letter))  # convert to 0-indexed
        return pairs

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def run_filter(self):
        try:
            absent = self._parse_letters(self.entry_absent.get())
            fixed_pairs = self._parse_position_pairs(self.entry_fixed.get(), "Correct position")
            present_pairs = self._parse_position_pairs(self.entry_present.get(), "Wrong position")
        except ValueError as e:
            show_error(self.root, "Invalid input", str(e))
            return

        self.wf.reset()
        self.wf.add_absent(absent)
        for pos, letter in fixed_pairs:
            self.wf.add_fixed(pos, letter)
        for pos, letter in present_pairs:
            self.wf.add_present(letter, pos)

        results = self.wf.filter()
        self.count_label.config(text=f"{len(results)} possible word(s)")
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, "\n".join(results))

    def reset_form(self):
        self.entry_absent.delete(0, tk.END)
        self.entry_fixed.delete(0, tk.END)
        self.entry_present.delete(0, tk.END)
        self.wf.reset()
        self.count_label.config(text="0 possible words")
        self.text_result.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    WordleFilterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()