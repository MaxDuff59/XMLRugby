import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pyrugga as prg
import seaborn as sns
import pandas as pd
import numpy as np
import warnings
import os
import glob

pd.set_option('display.max_columns', None)
warnings.filterwarnings("ignore")

def extract(file_path):
        
    with open(file_path, 'r') as file:
        xml_content = file.read()

    root = ET.fromstring(xml_content)

    match_data, team_data, game_infos = [], [], []

    for fxid in root:
        for child in fxid:
            if child.tag == 'MatchData':
                for action_row in child:
                    match_data.append(action_row.attrib)
            elif child.tag == 'TeamData':
                for team_row in child:
                    team_data.append(team_row.attrib)
            elif child.tag == 'FixData':
                for team_info in child:
                    game_infos.append(team_info.attrib)

    match_data_df, team_data_df, game_infos_df = pd.DataFrame(match_data), pd.DataFrame(team_data), pd.DataFrame(game_infos)[['FxDate','FxWeek','hometeam','HTFTSC','awayteam','ATFTSC']]

    match_data_df[['action','ActionType','Actionresult'] + [col for col in match_data_df.columns if 'qualifier' in col]] = match_data_df[['action','ActionType','Actionresult'] + [col for col in match_data_df.columns if 'qualifier' in col]].astype('int')

    unique_club_team = team_data_df[['Club', 'TEAMNAME']].drop_duplicates()
    club_team_dict = dict(zip(unique_club_team['Club'], unique_club_team['TEAMNAME']))
    player_name_dict = dict(zip(team_data_df['PLID'], team_data_df['PLFORN'] + ' ' + team_data_df['PLSURN']))

    match_data_df.insert(7,'team',match_data_df['team_id'].map(club_team_dict)) 
    match_data_df.insert(8,'player',match_data_df['PLID'].map(player_name_dict)) 

    dico_action = {6:'Lineout Throw',15:"Possession",26:"Sequence",5:"Scrum",23:"Ruck",24:"Maul",44:"Counter Attack",45:"Defensive Exit",46:"Attacking 22 Entry",17:"Clock Stoppage",14:"Restart Kick",9:"Try",12:"Lineout Throw",27:"Lineout Catch",7:"Penalty",21:"Card",1:"Carry",10:"Attacking Quality",3:"Pass",18:"Collection",4:"Kick",11:"Goal Kick",2:"Tackle",12:"Missed Tackle",8:"Turnover",20:"Referee Review",40:"Defensive Action",41:"Player Leaves Field",42:"Player Enters Field",43:"Ruck OOA",28:"Offensive Scrum",29:"Defensive Scrum",47:"Playmaker Options"}

    dico_qualifier = {101: 'One Out Drive',102: 'Pick and Go',103: 'Other Carry',104: 'Kick Return',105: 'Restart Return',106: 'Support Carry',107: 'Tackled Dominant',108: 'Tackled Neutral',109: 'Crossed Gain line',110: 'Neutral Gain line',111: 'Failed Gain line',112: 'Initial Break',113: 'Supported Break',116: 'Defender Beaten',117: 'Try Scored',118: 'Other',119: 'Error',120: 'Kick',121: 'Pass',122: 'Off Load',124: 'Pen Conceded',128: 'Own Player',129: 'To Ground',130: 'To Opposition',142: 'Chase Tackle',143: 'Cover Tackle',144: 'Line Tackle',145: 'Guard Tackle',146: 'Edge Tackle',147: 'Other Tackle',148: 'Penalty Kick',151: 'Offload',153: 'Complete',154: 'Forced in Touch',155: 'Offload Allowed',156: 'Turnover Won',157: 'Pen Conceded',158: 'Try Saver',159: 'Sack',160: 'Passive',161: 'Missed',162: 'Bumped Off',163: 'Stepped',164: 'Outpaced',165: 'Positional',166: 'Tackled',167: 'Clean Break',168: 'Try',169: 'Complete',172: 'Break',173: 'Forward',174: 'Incomplete',175: 'Intercepted',176: 'Key',177: 'Off Target',178: 'Try',180: 'Error',185: 'Kick in Play',186: 'Kick in Play (Own 22)',187: 'Bomb',
    188: 'Chip',189: 'Cross Pitch',190: 'Territorial',191: 'Low',192: 'Kick in Touch (Bounce)',193: 'Kick in Touch (Full)',194: 'Error – Charged Down',195: 'Error – Out of Play',196: 'Error – Territorial Loss',197: 'Error – Dead Ball',198: 'Caught Full',199: 'Collected Bounce',200: 'In Goal',207: 'Catch and Drive',208: 'Catch and Pass',209: 'Won Penalty Try',210: 'Penalty Won',211: 'Off the Top',214: 'Offence',215: 'Defence',216: 'Not Releasing',221: 'Offside',222: 'Collapsing Maul',223: 'Lineout Offence',224: 'Off Feet at Ruck',225: 'Not Rolling Away',226: 'Foul Play – Foot Contact',227: 'Foul Play – Mid Air Tackle',228: 'Foul Play – High Tackle',229: 'Foul Play – Other',236: 'No Action',237: 'Yellow Card',238: 'Red Card',241: 'Penalty Try',244: 'Video Review',245: 'Advantage',246: 'Yellow Card',247: 'Red Card',249: 'Attempted Intercept',250: 'Bad Offload',251: 'Bad Pass',252: 'Carried Over',253: 'Carried in Touch',254: 'Dropped Ball Unforced',255: 'Forward Pass',256: 'Lost Ball Forced',257: 'Accidental Offside',258: 'Lost in Ruck or Maul',259: 'Reset',260: 'Other Error',261: 'Kick Error',262: 'Failure to Find Touch',268: 'Interception',269: 'In Goal Touchdown',270: 'Mark',271: 'Attacking Catch',272: 'Attacking Loose Ball',273: 'Defensive Catch',274: 'Defensive Loose Ball',275: 'Restart Catch',276: 'Jackal',277: 'Success',278: 'Fail',281: '50m Restart',282: '22m Restart',284: 'Restart Retained',285: 'Restart Opp Error',286: 'Restart Opp Collection',287: 'Restart Own Error',288: 'Long Restart',289: 'Short Restart',295: 'Conversion',296: 'Drop Goal',297: 'Penalty Goal',298: 'Goal Missed',299: 'Goal Kicked',305: '22m Restart',306: 'Lineout',307: '50m Restart',308: 'Turnover Won',309: 'Scrum',310: 'Tap Pen',311: 'Kick Return',312: 'Free Kick',313: 'Drop Goal',314: 'Try',315: 'Kick Out of Play',316: 'Pen Won',317: 'Scrum',318: 'Turnover',319: 'Pen Con',320: 'Other',321: 'End of Play',333: 'Video Ref Awarded',334: 'Video Ref Disallowed',343: 'Non Playing Personnel',346: 'Box',347: 'Touch Kick',348: 'Lineout Steal',349: '22m Restart Retained',350: '50m Restart Retained',351: 'Kick in Play',352: 'Other Review',353: 'Won Outright',354: 'Won Try',356: 'Won Free Kick',
    357: 'Won Penalty',358: 'Lost Outright',359: 'Lost Pen Con',360: 'Lost Free Kick',361: 'Lost Reversed',362: 'Anti-Clockwise',363: 'Clockwise',364: 'Positive',365: 'Neutral',366: 'Negative',367: 'Scrum Half Pass',368: 'Scrum Half Kick',369: 'Scrum Half Run',370: 'No 8 Pick Up',371: 'Throw Front',372: 'Throw Middle',373: 'Throw Back',374: 'Throw 15m+',375: 'Throw Quick',376: 'Won Clean',377: 'Won Tap',378: 'Won Penalty',379: 'Won Free Kick',380: 'Won Other',381: 'Lost Not Straight',382: 'Lost Clean',383: 'Lost Free Kick',384: 'Lost Penalty',385: 'Lost Other',386: 'Lineout Win Front',387: 'Lineout Win Middle',388: 'Lineout Win Back',389: 'Lineout Win 15m+',390: 'Lineout Win Quick',391: 'Lineout Steal Front',392: 'Lineout Steal Middle',393: 'Lineout Steal Back',394: 'Lineout Steal 15m+',395: 'Lineout Steal Quick',396: 'Clean Catch',397: 'Clean Tap',398: 'Ineffective Tap',399: 'Error Missed Take',400: 'Error Dropped Take',401: 'Won Outright',402: 'Lost Outright',403: 'Penalty Won',404: 'Penalty Conceded',405: 'Try Scored',406: 'Penalty Try',407: 'Start Period',409: 'Tackled Ineffective',410: 'No 8 Pass',411: 'Turnover (Scrum)',412: 'Scrum Steal',413: 'Kick Error',414: 'Kick in Goal',415: 'Own Lineout',416: 'Kick in Touch',
    417: 'Lost Handling Error',418: 'Lost Not 5m',419: 'Lost Overthrown',420: 'Catch and Run',433: 'Barging',434: 'Obstruction',435: 'Offside',436: 'Taking Man in Air',437: 'Tap Back',438: 'Charge Down',439: 'Accidental Knock On',440: 'Referee Obstruction',441: 'Assist',442: 'Offside at Ruck - Att',443: 'Offside at Ruck - Def',444: 'Offside in General Play',445: 'Offside at Restart',452: 'Unplayable',453: 'Delaying the Throw',454: 'Closing the Gap',455: 'Early Lift',456: 'Wrong Numbers',460: 'Dominant Contact',461: 'Neutral Contact',462: 'Ineffective Contact',464: '5 Second Rule',467: 'Ineffective',473: 'Dominant Tackle',474: 'Neutral Tackle',475: 'Ineffective Tackle',500: '0 Tacklers Committed',501: '1 Tackler Committed',502: '2 Tacklers Committed',503: '3 Tacklers Committed',504: '4+ Tacklers Committed',526: 'Try Assist',527: 'Break Assist',528: 'Decoy',529: 'Snake',530: 'Line Break',531: 'Kick Line Break',532: 'Intercepted Break',533: 'Missed Left',534: 'Missed Right',535: 'Hit Left Post',536: 'Hit Right Post',537: 'Hit Crossbar',538: 'Dropped Short',539: 'Charged Down',540: 'Goal Line Restart',542: 'Foul Play',543: 'Professional Foul',544: 'Dissent',545: 'Fighting',546: 'Persistent Infringement',547: 'Stamping',548: 'Over Previous Gainline',549: 'Behind Previous Gainline',550: 'Equal to Previous Gainline',551: 'N/A Gainline',552: '0-1 Seconds Ruck Speed',553: '1-2 Seconds Ruck Speed',554: '2-3 Seconds Ruck Speed',555: '3-4 Seconds Ruck Speed',556: '4-5 Seconds Ruck Speed',557: '5-6 Seconds Ruck Speed',558: '6+ Seconds',559: 'N/A Ruck Speed',560: 'Tackle Arrival',561: 'Aerial Kick Contest',562: 'Tactical',563: 'Injury',564: 'Blood Replacement',565: 'Concussion Replacement',566: 'Front Row Replacement',567: 'Reversal Blood Replacement',568: 'Reversal Concussion Replacement',569: 'Reversal Front Row Replacement',570: 'Yellow Card',571: 'Red Card Replacement',572: 'Cleaned Out',573: 'Failed Clearout',574: 'Secured',575: 'Attended',576: 'Nuisance',577: 'Not Clearing',578: 'Got Cleaned Out',579: 'Turnover Won',580: 'Penalty Won',581: 'Penalty Conceded',583: 'Own Team 1st Entry',584: 'Own Team 2nd Entry',585: 'Own Team 3rd Entry',586: 'Own Team 4th Entry',587: 'Own Team 5th+ Entry',588: 'OOA Entry 1st Entry- Att',589: 'OOA Entry 2nd Entry- Att',590: 'OOA Entry 3rd Entry- Att',591: 'OOA Entry 4th Entry- Att',592: 'OOA Entry 5th Entry- Att',593: 'OOA Entry 6th Entry- Att',594: 'OOA Entry 7th Entry- Att',595: 'OOA Entry 8th Entry- Att',596: 'OOA Entry 9th Entry- Att',597: 'OOA Entry 10th Entry- Att',598: 'OOA Entry 11th Entry- Att',599: 'OOA Entry 12th Entry- Att',600: 'OOA Entry 13th Entry- Att',601: 'OOA Entry 14th Entry- Att',602: 'OOA Entry 15th Entry- Att',603: 'OOA Entry 1st Entry- Def',604: 'OOA Entry 2nd Entry- Def',605: 'OOA Entry 3rd Entry- Def',606: 'OOA Entry 4th Entry- Def',607: 'OOA Entry 5th Entry- Def',608: 'OOA Entry 6th Entry- Def',609: 'OOA Entry 7th Entry- Def',610: 'OOA Entry 8th Entry- Def',611: 'OOA Entry 9th Entry- Def',612: 'OOA Entry 10th Entry- Def',613: 'OOA Entry 11th Entry- Def',614: 'OOA Entry 12th Entry- Def',615: 'OOA Entry 13th Entry- Def',616: 'OOA Entry 14th Entry- Def',617: 'OOA Entry 15th Entry- Def',618: 'Outcome – Drop Goal',619: 'Outcome – Kick To Opposition',620: 'Outcome – Kicked Out',621: 'Outcome – Lineout Won',622: 'Outcome – Penalty Conceded',623: 'Outcome – Penalty Won',624: 'Outcome – Scrum Won',625: 'Outcome – Try Scored',626: 'Outcome – Turnover',628: 'Failed Exit From 22',629: 'Carried out of 22',630: 'Kicked out of 22',631: 'General Catch',632: 'Attacking OOA',633: 'Defensive OOA',635: 'Captains Referral – Upheld',636: 'Captains Referral – Overturned',637: 'Captains Referral - Inconclusive',638: '22 Entry Outcome – Drop Goal',639: '22 Entry Outcome – Kick Turnover',640: '22 Entry Outcome – Lineout Won',641: '22 Entry Outcome – Penalty Conceded',642: '22 Entry Outcome – Penalty Goal Attempt',643: '22 Entry Outcome – Penalty Won',644: '22 Entry Outcome – Scrum Won',645: '22 Entry Outcome – Try',646: '22 Entry Outcome - Turnover',647: '22 Entry Points – Drop Goal',648: '22 Entry Points – Penalty Goal',649: '22 Entry Points – Penalty Try',650: '22 Entry Points – Try and Conversion',651: '22 Entry Points – Try without Conversion',652: '22/50',653: '50/22',654: 'Goal Line Restart',655: 'Goal Line Restart Retained',656: 'First Receiver',657: 'Second Receiver',658: 'Third Receiver',659: 'Wide Left Open Movement',660: 'Wide Right Open Movement',661: 'Mid Left Open Movement',662: 'Mid Right Open Movement',663: 'Close left Open Movement',664: 'Close Right Open Movement',665: 'Close Left Blindside Movement',666: 'Close Right Blindside Movement',667: 'Tight Left Open Movement',668: 'Tight Right Open Movement',669: 'Tight Left Blindside Movement',670: 'Tight Right Blindside Movement',671: 'Halfback at Breakdown',672: 'Acting Halfback at Breakdown',673: 'Playmaker Option - Carry',674: 'Playmaker Option - Kick',
    675: 'Playmaker Option - Pass',676: 'N/A Movement',677: 'Error on Attack',678: 'Error on Defence',679: 'Short Pass',680: 'Long Pass',681: 'Left Pass',682: 'Right Pass',683: 'Enters into Opposition 22',684: 'Fails to enter into Opposition 22',685: 'Starts inside Opposition 22'}

    match_data_df['action'] = match_data_df['action'].map(dico_action)
    team_data_df.insert(6,'player',team_data_df['PLFORN'] + ' ' + team_data_df['PLSURN'])

    for col in ['ActionType','Actionresult'] + [col for col in match_data_df.columns if 'qualifier' in col]:
        match_data_df[col] = match_data_df[col].map(dico_qualifier)

    match_data_df['time_length'] = match_data_df['ps_endstamp'].astype('float').astype('int') - match_data_df['ps_timestamp'].astype('float').astype('int')
    match_data_df['zone_terrain'] = np.select([match_data_df.x_coord.astype('int') <= 22,(match_data_df.x_coord.astype('int') > 22) & (match_data_df.x_coord.astype('int') <= 50),(match_data_df.x_coord.astype('int') > 50) & (match_data_df.x_coord.astype('int') <= 78),match_data_df.x_coord.astype('int') > 78],['0-22','22-50','50-22','22-0'])

    class DataFrames:
        def __init__(self, df1, df2, df3):
            self.df1 = df1
            self.df2 = df2
            self.df3 = df3

    return DataFrames(match_data_df, team_data_df, game_infos_df)

