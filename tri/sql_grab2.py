import sqlite3 as db
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
import pandas_datareader.data as web
import datetime
import fix_yahoo_finance as yf
import pyodbc
yf.pdr_override()
cnx = db.connect('./tri/test.sqlite')

query = '''SELECT
-- UNIQUE
  T1.[SPEC_ID] AS InspectionID,
  T1.CSTCOMMENTSTX,
  convert(date,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) AS InspectionCompletionDate
  ,T1.CSTCOMPLETIONDA,
  convert(date,dateadd(ms, convert(bigint,T1.CSTINSPECTIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTINSPECTIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) AS InspectionDate,
  T1.CSTINSPECTIONDA,
  convert(int,dateadd(ms, convert(bigint,T1.CSTINSPECTIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTINSPECTIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))+1 AS InspectionDate_SQL
  ,convert(date,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0'))) AS InspectionStartDate
  ,convert(int,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) - convert(int,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0'))) as DAY_DIFF,
  CASE WHEN    dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')) IS NULL
  THEN    convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0')))
  ELSE convert(int,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) - convert(int,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0')))
  END AS Inspection_NumDaysToClose,
  T1.cstErgonomicReasonLI as [Reason for Inspection],
  T1.CSTINSPECTIONTYPETX as [Inspection Type],
  T1.CSTINSPECTORTX as Inspector,
  T1.cstCommentsTX as [Inspection Comments],
  T1.TRIBUILDINGTX as [Building],
  T1.TRIFLOORTX as [Floor],
  T1.TRINAMETX as [Inspection Name],
  T1.TRIREQUESTEDFORTX as [Requested For],
  T1.TRISPACETX as [Space],
  T1.TRISTATUSCL as [Inspection Status],
  T1.TRIIDTX AS [Inspection ID]
,T1.cstChronicDiscomfortLI as [Chronic Discomfort]
,T1.cstPreExistingLI as [PreExisting]
,T1.cstErgoIssuesTX as [Ergo Issues]
,T1.cstPhysicianSeenLI as [Physician Seen]
,T1.cstErgoDiscomfortLI as [Ergo Discomfort]
,t1.cstFollowUpDA as [Followup]
,T1.cstLabRoomTX as [Lab Room]
,t1.cstvivariumlocationli as [Vivarium Location]
,t1.cstOfficeTypeBL as [Office Type]
,t1.cstVivariumTypeBL as [Vivarium Type]
,t1.cstLabTypeBL as [Lab Type]
,t2.cstquestioncategorytx as [Question Category]
,t2.cstquestionnumbernu as [Question Number]
,t2.trinametx as [Question]
,t2.cstresponsetx as [Response]
,t3.trispacetx as [Lab Space]
,t5.trinametx as [Gatekeeper Organization]
--Combo
,
case
when t3.cstactionrequiredli = 'Create Work Order' and t4.tristatuscl<>'Completed'then
convert(int,current_timestamp+1)-
convert(int,dateadd(ms, convert(bigint,t4.tricreatedsy)%(3600*24*1000) ,dateadd(day,
        convert(bigint,t4.tricreatedsy)/(3600*24*1000), '1970-01-01 00:00:00.0')))
when t4.tricreatedsy is null and t3.cstactionrequiredli = 'User Action Required' and t3.tristatuscl <> 'Completed' then
convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.cstInspectionDA)%
        (3600*24*1000) ,dateadd(day, convert(bigint,T1.cstInspectionDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))
when t4.tricreatedsy is null and t3.cstactionrequiredli = 'User Action Required' and t3.tristatuscl = 'Completed' and t3.CSTDATERESOLVEDDA is not null then
convert(int,dateadd(ms, convert(bigint,t3.cstdateresolvedda)%(3600*24*1000) ,dateadd(day,
        convert(bigint,t3.cstdateresolvedda)/(3600*24*1000), '1970-01-01 00:00:00.0')))
-convert(int,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day,
         convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))
when t4.tricreatedsy is null  and t3.cstactionrequiredli = 'User Action Required' and t3.tristatuscl = 'Completed' and t3.CSTDATERESOLVEDDA is null then 1
when t4.tricreatedsy is null and t3.cstactionrequiredli = 'Corrected On-site' then 1
when t4.tricreatedsy is not null and t4.tristatuscl = 'Completed' then
convert(int,dateadd(ms, convert(bigint,t4.triActualEndDT)%(3600*24*1000) ,dateadd(day,
        convert(bigint,t4.triActualEndDT)/(3600*24*1000), '1970-01-01 00:00:00.0')))
-convert(int,dateadd(ms, convert(bigint,t4.TRIACTUALSTARTDT)%(3600*24*1000) ,dateadd(day,
         convert(bigint,t4.TRIACTUALSTARTDT)/(3600*24*1000), '1970-01-01 00:00:00.0')))
else
convert(int,current_timestamp+1)-
convert(int,dateadd(ms, convert(bigint,t1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day,
        convert(bigint,t1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))
end as Duration
,
case
when t3.cstactionrequiredli = 'Create Work Order' and t4.tristatuscl<>'Completed'then
convert(date,dateadd(ms, convert(bigint,t4.tricreatedsy)%(3600*24*1000) ,dateadd(day,
        convert(bigint,t4.tricreatedsy)/(3600*24*1000), '1970-01-01 00:00:00.0')))
when t4.tricreatedsy is null and t3.cstactionrequiredli = 'User Action Required' and t3.tristatuscl <> 'Completed' then
convert(date,dateadd(ms, convert(bigint,T1.cstInspectionDA)%(3600*24*1000) ,dateadd(day,
        convert(bigint,T1.cstInspectionDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))
when t4.tricreatedsy is null and t3.cstactionrequiredli = 'User Action Required' and t3.tristatuscl = 'Completed' and t3.CSTDATERESOLVEDDA is not null then
convert(date,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day,
        convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))
when t4.tricreatedsy is null  and t3.cstactionrequiredli = 'User Action Required' and t3.tristatuscl = 'Completed' and t3.CSTDATERESOLVEDDA is null then
convert(date,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day,
        convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))
when t4.tricreatedsy is null and t3.cstactionrequiredli = 'Corrected On-site' then
convert(date,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day,
        convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))

when t4.tricreatedsy is not null and t4.tristatuscl = 'Completed' then
convert(date,dateadd(ms, convert(bigint,t4.TRIACTUALSTARTDT)%(3600*24*1000) ,dateadd(day,
        convert(bigint,t4.TRIACTUALSTARTDT)/(3600*24*1000), '1970-01-01 00:00:00.0')))
else
convert(date,dateadd(ms, convert(bigint,t1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day,
        convert(bigint,t1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0')))
end as [Task Date]
----Combination
,null as [Hand Dominance]
,case
when t3.trispacetx is not null then t3.trispacetx
when WTH_SPACE.trinametx is null then LA_SPACE.trinametx
--add another case for wth_space
when
t4.triWorkingLocationTX is null and LA_SPACE.trinametx is null then WTH_SPACE.trinametx
else right(t4.triWorkingLocationTX, charindex('\', reverse(t4.triWorkingLocationTX)) - 1)
end as [Task Space]
,WTH_SPACE.trinametx as WTH_SPACE
,LA_SPACE.trinametx as LA_SPACE
,t4.trispacetx as WT_SPACE
,case when t4.triDescriptionTX is null then t3.triDescriptionTX
else t4.triDescriptionTX
end as [Task Description]
, case when t4.triResolutionDescrTX is null then t3.cstcorrectionresponset
 else t4.triResolutionDescrTX
 end as [Task Resolution]
,T3.cstactionrequiredli as [Action Required],
case
 	when t3.cstActionRequiredLI = 'Corrected On-site'  then 'Completed'
    when t20.trinametx is not null and t3.tristatuscl = 'Reassigned' then 'Reassignment Requested'
    when t20.trinametx is not null then 'Assigned'
--     when t20.trinametx is not null and t3.tristatuscl = 'Reassigned' then 'Reassignment Requested'
-- 	when t20.trinametx is not null and t3.tristatuscl = 'Created' then 'Assigned'
-- 	when t20.trinametx is not null and t3.tristatuscl = 'Completed' then 'Completed'
    when t20.trinametx is null and t3.cstActionRequiredLI not like '%Create%' then 'Unassigned'
    when t4.triResourceAssignmen is null then NULL
     else t4.triResourceAssignmen
     end as [Resource Assignment]
-- 	,case
-- 	when t3.cstActionRequiredLI = 'Corrected On-site' then 'Completed'
--     when t4.triResourceAssignmen is null and t20.trinametx is null then EQUIPWT.triResourceAssignmen
--     when t20.trinametx is not null then 'Assigned'
--     when t20.trinametx is null and EQUIPWT.triResourceAssignmen is null then  t4.triResourceAssignmen
--     else 'Null'
--     end as Resource_Assignment
,    case
    when t3.cstactionrequiredli = 'Create Work Task' then t4.tristatuscl
	when t4.tristatuscl is null then t3.tristatuscl
    else t4.TRISTATUSCL
    end
    as [Task Status],
case
   when t20.trinametx is null and RESPPERSON.trinametx is not null then RESPPERSON.trinametx
   else t20.trinametx
   end as [Responsible Person]
  ,case when t20.triEmailTX is null and RESPPERSON.triEmailTX is not null then RESPPERSON.triEmailTX
  else t20.triemailtx
  end as [Responsible Person Email]
,case when t50.trinametx is null then t5001.trirecordnamesy
   else t50.trinametx
   end as [Organization Name]
,case
  when t20.trinametx is null then WTRESRC.trinametx
  else t20.trinametx
  end as [Assigned Resource Name]
,case
  when t20.trinametx is null then WTRESRC.triemailtx
  else t20.triemailtx
  end as [Assigned Resource Email]
,convert(varchar(100),t3.spec_id) as [WTH Spec ID]
,convert(varchar(100),t4.spec_id) as [Task ID]
,case when
	convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) < 15 then '1-15 days'
    when
    convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) >= 15 and
    convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) < 30 then '15-30 days'
    when
    convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.CSTCOMPLETIONDA)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.CSTCOMPLETIONDA)/(3600*24*1000), '1970-01-01 00:00:00.0'))) >=30 then '30+ days'
    when T1.CSTCOMPLETIONDA is null and
	convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0'))) < 15 then '1-15 days'

    when T1.CSTCOMPLETIONDA is null and
	convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0'))) >= 15 and
    convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0'))) < 30 then '15-30 days'

    when T1.CSTCOMPLETIONDA is null and
	convert(int,current_timestamp+1)-convert(int,dateadd(ms, convert(bigint,T1.SYS_CREATEDTIME)%(3600*24*1000) ,dateadd(day, convert(bigint,T1.SYS_CREATEDTIME)/(3600*24*1000), '1970-01-01 00:00:00.0'))) >=30 then '30+ days'
    else '0'
    end as [Aging Bucket]
  ,t3.cstbenchtx as Bench
,CASE
WHEN T3.cstriskli like '%High%' then 'High'
WHEN T3.cstriskli like '%Med%' then 'Medium'
WHEN T3.cstriskli like '%Low%' then 'Low'
else T4.triPriorityClassCL
end as [Risk Level]
,t4.triMatrixRequestClas as [Request Class]
,NULL as [Equipment]
,T900.trinametx as [Responsible Department]

,case
--
when T50.trinametx is null and t900.trinametx is not null then t900.trinametx
when T50.trinametx is null and t900.trinametx is null and t3.triorganizationtx is not null then t3.triorganizationtx
when T50.trinametx is null and t900.trinametx is null and t3.triorganizationtx is null then t5001.trinametx
else T50.trinametx
end as [Audited Department]



--TABLES
FROM T_CSTINSPECTION T1
LEFT JOIN IBS_SPEC_ASSIGNMENTS T9 ON T1.SPEC_ID = T9.SPEC_ID
	AND T9.ASS_SPEC_CLASS_TYPE = 24541
	AND T9.ASS_SPEC_TEMPLATE_ID = 10031841
	AND T9.ASS_TYPE = 'Has'
LEFT JOIN T_CSTQUESTION T2 ON T9.ASS_SPEC_ID = T2.SPEC_ID
	AND T2.SYS_OBJECTID > 0
LEFT JOIN IBS_SPEC_ASSIGNMENTS T10 ON T2.SPEC_ID = T10.SPEC_ID
	AND T10.ASS_SPEC_CLASS_TYPE = 24541
	AND T10.ASS_SPEC_TEMPLATE_ID = 10031837
	AND T10.ASS_TYPE = 'Has'
LEFT JOIN T_CSTWORKTASKHELPER T3 ON T10.ASS_SPEC_ID = T3.SPEC_ID
	AND T3.SYS_OBJECTID > 0
LEFT JOIN IBS_SPEC_ASSIGNMENTS t1300 ON T3.SPEC_ID = t1300.SPEC_ID
	AND t1300.ASS_SPEC_CLASS_TYPE = 6
	AND t1300.ASS_SPEC_TEMPLATE_ID = 10002873
	AND t1300.ASS_TYPE = 'Has Location'
LEFT JOIN T_TRISPACE WTH_SPACE ON t1300.ASS_SPEC_ID = WTH_SPACE.SPEC_ID
	AND WTH_SPACE.SYS_OBJECTID > 0
LEFT JOIN IBS_SPEC_ASSIGNMENTS T120 ON T3.SPEC_ID = T120.SPEC_ID
	AND T120.ASS_SPEC_CLASS_TYPE = 10
	AND T120.ASS_SPEC_TEMPLATE_ID = 103804
	AND T120.ASS_TYPE = 'Has'
LEFT JOIN T_ORGANIZATION T50 ON T120.ASS_SPEC_ID = T50.SPEC_ID
	AND T50.SYS_OBJECTID > 0
LEFT JOIN IBS_SPEC_ASSIGNMENTS T11 ON t3.SPEC_ID = T11.SPEC_ID
	AND T11.ASS_SPEC_CLASS_TYPE = 29
	AND T11.ASS_SPEC_TEMPLATE_ID = 10008284
	AND T11.ASS_TYPE = 'Has'
LEFT JOIN T_TRIWORKTASK T4 ON T11.ASS_SPEC_ID = T4.SPEC_ID
	AND T4.SYS_OBJECTID > 0
 LEFT JOIN IBS_SPEC_ASSIGNMENTS T10003 ON T4.SPEC_ID = T10003.SPEC_ID
 	AND T10003.ASS_SPEC_CLASS_TYPE = 7
 	AND T10003.ASS_SPEC_TEMPLATE_ID = 106402
 	AND T10003.ASS_TYPE = 'ffxStaff'
 LEFT JOIN T_TRIPEOPLE WTRESRC ON T10003.ASS_SPEC_ID = WTRESRC.SPEC_ID
 	AND WTRESRC.SYS_OBJECTID > 0
 LEFT JOIN IBS_SPEC_ASSIGNMENTS T5000 ON T4.SPEC_ID = T5000.SPEC_ID
 	AND T5000.ASS_SPEC_CLASS_TYPE = 10
 	AND T5000.ASS_SPEC_TEMPLATE_ID = 103804
 	AND T5000.ASS_TYPE = 'Customer Of'
 LEFT JOIN T_ORGANIZATION T5001 ON T5000.ASS_SPEC_ID = T5001.SPEC_ID
 	AND T5001.SYS_OBJECTID > 0
LEFT JOIN IBS_SPEC_ASSIGNMENTS T110000 ON t4.SPEC_ID = T110000.SPEC_ID
	AND T110000.ASS_SPEC_CLASS_TYPE = 6
	AND T110000.ASS_SPEC_TEMPLATE_ID = 10002873
	AND T110000.ASS_TYPE = 'Has Primary Location'
LEFT JOIN T_TRISPACE LA_SPACE ON T110000.ASS_SPEC_ID = LA_SPACE.SPEC_ID
	AND LA_SPACE.SYS_OBJECTID > 0
 LEFT JOIN IBS_SPEC_ASSIGNMENTS T12 ON T4.SPEC_ID = T12.SPEC_ID
 	AND T12.ASS_SPEC_CLASS_TYPE = 10
 	AND T12.ASS_SPEC_TEMPLATE_ID = 103804
 	AND T12.ASS_TYPE = 'Primary Organization'
 LEFT JOIN T_ORGANIZATION T5 ON T12.ASS_SPEC_ID = T5.SPEC_ID
 	AND T5.SYS_OBJECTID > 0
 LEFT JOIN IBS_SPEC_ASSIGNMENTS T19 ON T3.SPEC_ID = T19.SPEC_ID
 	AND T19.ASS_SPEC_CLASS_TYPE = 7
 	AND T19.ASS_SPEC_TEMPLATE_ID = 106402
 	AND T19.ASS_TYPE = 'Has Responsible'
 LEFT JOIN T_TRIPEOPLE t20 ON T19.ASS_SPEC_ID = t20.SPEC_ID
 	AND T20.SYS_OBJECTID > 0
 LEFT JOIN IBS_SPEC_ASSIGNMENTS T1200 ON t20.SPEC_ID = T1200.SPEC_ID
 	AND T1200.ASS_SPEC_CLASS_TYPE = 10
 	AND T1200.ASS_SPEC_TEMPLATE_ID = 103804
 	AND T1200.ASS_TYPE = 'Primary Organization'
 LEFT JOIN T_ORGANIZATION T900 ON T1200.ASS_SPEC_ID = T900.SPEC_ID
 	AND T900.SYS_OBJECTID > 0
 LEFT JOIN IBS_SPEC_ASSIGNMENTS T130 ON t4.SPEC_ID = T130.SPEC_ID
     AND T130.ASS_SPEC_CLASS_TYPE = 7
     AND T130.ASS_SPEC_TEMPLATE_ID = 106402
     AND T130.ASS_TYPE = 'Has Responsible'
 LEFT JOIN T_TRIPEOPLE RESPPERSON ON T130.ASS_SPEC_ID = RESPPERSON.SPEC_ID
     AND RESPPERSON.SYS_OBJECTID > 0
WHERE
T1.TRISTATUSCL <> 'Template'
and t1.cstinspectiontypetx ='Lab Audit'
AND (T1.triStatusCL NOT IN (
				'Template'
				,'Retired'
                ,'Created')
                OR
                t4.tristatuscl <> ' Retired'
	)
and T1.TRISTATUSCL not like 'Retired'
and t1.tristatuscl = 'Completed'
and t1.TRIBUILDINGTX <> 'Offsite'
and T1.CSTINSPECTORTX not in(
	'Matthew Varga',
    'Fred Chun',
    'Amir Karbasi',
    'Ramy El Khayat')
	AND T1.SYS_OBJECTID > 0
	and (t4.tristatuscl <> 'Retired' or t4.tristatuscl is null)
     	and (t3.tristatuscl <> 'Created' or t4.tristatuscl is null)'''

df = []
first_load = 0
if first_load == 1:
    sql_conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                              "Server=TARTRRG06SQLLRT;"
                              "Database=tridev;"
                              "UID=tritest;"
                              "PWD=tritest;")

    df = pd.read_sql(query, sql_conn)
    df.to_sql('tab', cnx, if_exists='replace', index=True)
else:
    query = 'select * from tab'
    df = pd.read_sql_query(query, cnx)
# people_count = df.groupby('TRINAMETX')['SPEC_ID'].nunique()
# print(people_count)
people_count = []
people_count = df.groupby('Inspector')['Inspection ID'].nunique().reset_index()
people_count.set_index('Inspector', inplace=True)

print(people_count.head(10))
# bleh = [i for i in people_count.Inspector]
# print(bleh)
print(people_count.loc['Kaila Hanley', 'Inspection ID'])
app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})  # noqa: E501

#make this a df
building_latlong=[
['building1',41.076471,-73.826029],
['building2' , 41.077473,-73.825487],
['building3' , 41.076717,-73.823464],
['building4' , 41.07913,-73.821598],
['building5' , 41.081048,-73.822823],
['building6' , 41.080082,-73.820267]]
buildings_header = ['Building','Latitude','Longitude']
buildings_df =  pd.DataFrame(building_latlong,columns = buildings_header).set_index('Building')
print(buildings_df)


app.layout = html.Div(children=[
    html.H1('''
        symbol to graph
    '''),
    html.Div(
        [
            html.Div(
                [
                    html.P('Choose:'),

                    dcc.Dropdown(id='inspectors',
                                 options=[{'label': index, 'value': index}
                                          for index, row in people_count.iterrows()],
                                 value=[ index 
                                 for index, row in people_count.iterrows()],
                                 multi=True
                                 )
                ]
            ),
            html.Div(
                [
                    dcc.Graph(id='example-graph')
                ],className= 'six columns'
            ),
            html.Div(
                [
                    dcc.Graph(id='example-graph-2')
                ],className= 'six columns'
            )
        ]
    )
])


@app.callback(
    Output('example-graph', 'figure'),
    [Input('inspectors', 'value')])
def update_image_src(selector):
    data = []
    for inspector in selector:
        data.append({'x': people_count.loc[inspector], 'y': people_count.loc[inspector, 'Inspection ID'],
                     'type': 'bar', 'name': inspector
                     })

    # if 'Kaila Hanley' in selector:
    #     data.append({'x': people_count.Inspector,
    #                  'y': people_count['Inspection ID'], 'type': 'bar', 'name': 'Kaila Hanley'})
    figure = {
        'data': data,
        'layout': {
            'title': 'Graph 1',
            'xaxis': dict(
                title='x Axis',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=20,
                    color='#7f7f7f'
                )),
            'yaxis': dict(
                title='y Axis',
                titlefont=dict(
                    family='Helvetica, monospace',
                    size=20,
                    color='#7f7f7f'
                ))
        }
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
