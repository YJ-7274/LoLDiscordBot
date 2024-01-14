from ast import alias
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch  
from yt_dlp import YoutubeDL
import asyncio
import random 
import responses
import praw

class functionality(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}

        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

     #searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return{'source':item, 'title':title}
        search = VideosSearch(item, limit=1)
        return{'source':search.result()["result"][0]["link"], 'title':search.result()["result"][0]["title"]}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable= "ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # infinite loop checking 
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable= "ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("```Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue)+2} -'{song['title']}'** added to the queue")  
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")  
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i+1} -" + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
    
    @commands.command(name="remove", help="Removes last song added to queue")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("```last song removed```")

    @commands.command(name="miscellanious functions", aliases=["msf"], help="keyword for some small fun commands")
    async def msf(self, ctx, *args):
        user_message = " ".join(args)

        async def send_message(user_message, is_private): 
            try: 
                response = responses.get_response(user_message)
                await ctx.message.author.send(response) if is_private else await ctx.message.channel.send(response)

            except Exception as e: 
                print (e) 
                
        if user_message[0] == '?':
            user_message = user_message[1:]
            await send_message(user_message, is_private= True)
        else:
            await send_message(user_message, is_private= False)
    
    @commands.command(name="memes", help="inserts the top 5 memes of the requested subreddit into the chat")
    async def memes(self, ctx, *args):
        reddit = praw.Reddit(client_id = "TnWvxUmpdviA1e6P835J0w", client_secret = "PZXvlz0dCSRWbGByMw_P-xBjSiSOvw", username = "TundraShredder855", 
                     password = "Armada855", user_agent = "TundraShredder")
        all_subs = []
        sub_name = "".join(args)
        subreddit1 = reddit.subreddit(sub_name)
        hot = subreddit1.hot(limit = 50)
        for submission in hot: 
            all_subs.append(submission)
        
        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url
        em = discord.Embed(title = name)
        em.set_image(url = url)
        await ctx.send(embed = em)

    @commands.command(name="randomRunes", help="generates a random combination of runes for your match. The subrunes are your choice ;D")
    async def randomRunes(self, ctx):
        big_Runes = ['Precision', 'Sorcery', 'Domination', 'Resolve', 'Inspiration']
        Precision_Keystones = ['Press The Attack', 'Conqueror', 'Lethal Tempo', 'Fleet Footwork']
        Sorcery_Keystones = ['Summon Aery', 'Arcane Comet', 'Phase Rush']
        Domination_Keystones = ['Electrocute', 'Predator', 'Dark Harvest', 'Hail of Blades']
        Resolve_Keystones = ['Grasp of the Undying','Aftershock','Guardian']
        Inspiration_Keystones = ['Glacial Augment','Unsealed Spellbook','First Strike']

        runes = random.sample(big_Runes,2)
        
        keystone = ''
        match runes[0]: 
            case 'Precision': 
                keystone += random.sample(Precision_Keystones, 1)[0]
            case 'Sorcery':
                keystone += random.sample(Sorcery_Keystones, 1)[0]
            case 'Domination':
                keystone += random.sample(Domination_Keystones, 1)[0]
            case 'Resolve':
                keystone += random.sample(Resolve_Keystones, 1)[0]
            case default:
                keystone += random.sample(Inspiration_Keystones, 1)[0]
            
        return_value = f'{runes[0]} + {runes[1]}: Keystone = {keystone}'
        await ctx.send(return_value)

    @commands.command(name="randomItems", help="generates a random combination of items for your match")
    async def randomItems(self, ctx):
        itempool = [
        "Abyssal Mask", "Anathema's Chains", "Archangel's Staff", "Ardent Censer", "Axiom Arc",
        "Banshee's Veil", "Black Cleaver", "Blade of the Ruined King", "Bloodsong", "Bloodthirster",
        "Bounty of Worlds", "Celestial Opposition", "Chempunk Chainsword", "Cosmic Drive", "Cryptbloom",
        "Dawncore", "Dead Man's Plate", "Death's Dance", "Dream Maker", "Echoes of Helia",
        "Eclipse", "Edge of Night", "Essence Reaver", "Experimental Hexplate", "Fimbulwinter",
        "Force of Nature", "Frozen Heart", "Guardian Angel", "Guinsoo's Rageblade", "Heartsteel",
        "Hextech Rocketbelt", "Hollow Radiance", "Horizon Focus", "Hubris", "Hullbreaker",
        "Iceborn Gauntlet", "Immortal Shieldbow", "Imperial Mandate", "Infinity Edge", "Jak'Sho, The Protean",
        "Kaenic Rookern", "Knight's Vow", "Kraken Slayer", "Liandry's Torment", "Lich Bane",
        "Locket of the Iron Solari", "Lord Dominik's Regards", "Luden's Companion", "Malignance", "Manamune",
        "Maw of Malmortius", "Mejai's Soulstealer", "Mercurial Scimitar", "Mikael's Blessing", "Moonstone Renewer",
        "Morellonomicon", "Mortal Reminder", "Muramana", "Nashor's Tooth", "Navori Quickblades",
        "Opportunity", "Phantom Dancer", "Profane Hydra", "Rabadon's Deathcap", "Randuin's Omen",
        "Rapid Firecannon", "Ravenous Hydra", "Redemption", "Riftmaker", "Rod of Ages",
        "Runaan's Hurricane", "Rylai's Crystal Scepter", "Seraph's Embrace", "Serpent's Fang", "Serylda's Grudge",
        "Shadowflame", "Shurelya's Battlesong", "Solstice Sleigh", "Spear of Shojin", "Spirit Visage",
        "Staff of Flowing Water", "Statikk Shiv", "Sterak's Gage", "Stormrazor", "Stormsurge",
        "Stridebreaker", "Sundered Sky", "Sunfire Aegis", "Terminus", "The Collector",
        "Thornmail", "Titanic Hydra", "Trailblazer", "Trinity Force", "Umbral Glaive",
        "Unending Despair", "Vigilant Wardstone", "Void Staff", "Voltaic Cyclosword", "Warmog's Armor",
        "Winter's Approach", "Wit's End", "Youmuu's Ghostblade", "Zaz'Zak's Realmspike", "Zeke's Convergence",
        "Zhonya's Hourglass"
        ]
        
        itemselection = random.sample(itempool, 6)
        return_value = f'{itemselection[0]} + {itemselection[1]} + {itemselection[2]} + {itemselection[3]} + {itemselection[4]} + {itemselection[5]}'
        await ctx.send(return_value)

    @commands.command(name="randomChamp", help="generates a random champ to select for your match")
    async def randomChamp(self, ctx):
        champPool = [
            "Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Amumu", "Anivia", "Annie", "Aphelios", "Ashe",
            "Aurelion Sol", "Azir", "Bard", "Bel'Veth", "Blitzcrank", "Brand", "Braum", "Briar", "Caitlyn", "Camille",
            "Cassiopeia", "Cho'Gath", "Corki", "Darius", "Diana", "Dr. Mundo", "Draven", "Ekko", "Elise", "Evelynn",
            "Ezreal", "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar", "Gragas", "Graves",
            "Gwen", "Hecarim", "Heimerdinger", "Hwei", "Illaoi", "Irelia", "Ivern", "Janna", "Jarvan IV", "Jax",
            "Jayce", "Jhin", "Jinx", "K'Sante", "Kai'Sa", "Kalista", "Karma", "Karthus", "Kassadin", "Katarina",
            "Kayle", "Kayn", "Kennen", "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", "Leona",
            "Lillia", "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai", "Master Yi", "Milio",
            "Miss Fortune", "Mordekaiser", "Morgana", "Naafiri", "Nami", "Nasus", "Nautilus", "Neeko", "Nidalee", "Nilah",
            "Nocturne", "Nunu & Willump", "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn",
            "Rakan", "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar", "Riven", "Rumble", "Ryze",
            "Samira", "Sejuani", "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion",
            "Sivir", "Skarner", "Sona", "Soraka", "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah", "Talon",
            "Taric", "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere", "Twisted Fate", "Twitch", "Udyr", "Urgot",
            "Varus", "Vayne", "Veigar", "Vel'Koz", "Vex", "Vi", "Viego", "Viktor", "Vladimir", "Volibear",
            "Warwick", "Wukong", "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone", "Yorick", "Yuumi", "Zac",
            "Zed", "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra"
        ]
        champSelection = random.sample(champPool, 1)
        return_value = f'{champSelection[0]}'
        await ctx.send(return_value)
    
    





