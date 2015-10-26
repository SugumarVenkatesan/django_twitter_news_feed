from django import template
from django.template import Library, Node, VariableDoesNotExist
from django.conf import settings
from datetime import datetime, timedelta

from MonitoringSystem.OITS.proposal_abstract.models import *
from MonitoringSystem.OITS.oi_request.models import *
from MonitoringSystem.OITS.oi.models import *
from MonitoringSystem.common.master.models import *
from MonitoringSystem.Utilities import Utility

register = Library()


#fill phase
def fill_phase(phase):
    str_phase = ''
    for each_phase in phase:
        str_phase = str_phase + '<option value=' + each_phase.pk + '>' + each_phase.name + '</option>'
    return str_phase


#fill tool
def fill_tool(tool, selected_id=''):
    str_tool = ''
    for each_tool in tool:
        if(selected_id == each_tool.pk):
            str_tool += '<option value="' + each_tool.pk + '" title="' + each_tool.name + '" selected="selected">' + each_tool.name + '</option>'
        else:
            str_tool += '<option value="' + each_tool.pk + '" title="' + each_tool.name + '" >' + each_tool.name + '</option>'
    return str_tool


#fill role
def fill_role(role, selected_id=''):
    str_role = ''
    for each_role in role:
        if(selected_id == each_role.pk):
            str_role += '<option value="' + each_role.pk + '" title="' + each_role.name + '" selected="selected">' + each_role.name + '</option>'
        else:
            str_role += '<option value="' + each_role.pk + '" title="' + each_role.name + '">' + each_role.name + '</option>'
    return str_role


#fill mode
def fill_mode(mode, selected_id=''):
    str_mode = ''
    for each_mode in mode:
        if(selected_id == each_mode.pk):
            str_mode += '<option value="' + each_mode.pk + '" selected="selected">' + each_mode.name + '</option>'
        else:
            str_mode += '<option value="' + each_mode.pk + '" >' + each_mode.name + '</option>'
    return str_mode


def fill_phase_mode(phasemode, selected_id=''):
    str_mode = ''
    for each_mode in phasemode:
        if(selected_id == each_mode.pk):
            str_mode += '<option value="' + each_mode.pk + '" selected="selected">' + each_mode.name + '</option>'
        else:
            str_mode += '<option value="' + each_mode.pk + '" >' + each_mode.name + '</option>'
    return str_mode


def fill_country(country, selected_id):
    str_country = ''
    for each_country in country:
        if(selected_id == each_country.pk):
            str_country += '<option value="' + each_country.pk + '" selected="selected">' + each_country.name + '</option>'
        else:
            str_country += '<option value="' + each_country.pk + '" >' + each_country.name + '</option>'
    return str_country


def truncchar(value, arg):
    if len(value) < arg:
        return value
    else:
        return value[:arg] + '...'


def fill_editmode_oirequest_details(id):
    if(id == ''):
        return ""
    oirequest_details_obj = OIRequest.objects.get(pk=id)
    service_type_details = OIRequestService.objects.filter(oi_request=oirequest_details_obj).order_by('service__code')
    phase_type_details = OIRequestPhaseEffort.objects.filter(oi_request_service__oi_request__id=id).order_by('phase__code')
    hiddendata = ''
    data = ''
    tblrows = ''
    for each_service in service_type_details:
        tblrows += generate_table(each_service.service.id, each_service.service.short_name, each_service, id)
    phase_type_details = OIRequestPhaseEffort.objects.filter(oi_request_service__oi_request__id=id).order_by('phase__code')
    return tblrows


def generate_table(i, tabname, each_service, id, include_div=False):
    tblrows = ''
    tblid = "servicetype" + i
    divid = "divservicetype" + i
    if(include_div):
        tblrows += '<div id="' + divid + '" class="oirequestservicetable">'
    tblrows += generate_total_budget(i, tabname, each_service)
    tblrows += '<div id="div_effort' + i + '">'
    tblrows += fill_editmode_phase_details(id, i)
    tblrows += '</div>'
    tblrows += '<input type="hidden" name="selected_phaseid' + i + '" id="selected_phaseid' + i + '" value=""/>'
    tblrows += '<input type="hidden" name="selected_phaseval' + i + '" id="selected_phaseval' + i + '" value=""/>'
    if(include_div):
        tblrows += '</div>'
    return tblrows


def generate_total_budget(i, tabname, each_service):
    phase = ProjectPhase.objects.all().filter(is_active=1).order_by('code')
    fillPhase = fill_phase(phase)
    mode = ProjectMode.objects.all().filter(is_active=1).order_by('name')
    phasetext = '<tr><td><label>Select the phase</label></td><td><select  class = "disablephase"  name="phase_list' + i + '" id="phase_list' + i + '" multiple="multiple" ><option value="all">All</option> '
    phasetext += fillPhase
    phasetext += '</select></td>'

    servicetext = '<select id="service_projectmode_' + i + '" name="service_projectmode_' + i + '" class="servicedisable" onchange="verifyphasemode(this);" ><option value="">--select--</option>'
    servicetext += fill_mode(mode, each_service.service_projectmode.id)
    servicetext += '</select>'

    tblrows = ''
    tblid = "tbltotal_budget" + i
    tblrows += '<table><tr><td><label>Service Start Date</label></td><td><input type="text" id="service_start_date' + i + '" name="service_start_date' + i + '" readonly="readonly" value="' + getdatetodisplay(each_service.service_start_date) + '" /></td>'
    tblrows += '<td><label>Service End Date</label></td><td><input type="text" id="service_end_date' + i + '" name="service_end_date' + i + '" readonly="readonly" value="' + getdatetodisplay(each_service.service_end_date) + '" /></td></tr>'
    tblrows += '<tr><td><label>Service Mode</label></td><td colspan="3">'
    tblrows += servicetext
    tblrows += '</td></tr>'
    tblrows += phasetext
    tblrows += '<td><label>Effort Type</label></td><td><select name="servicemode_' + i + '" id="servicemode_' + i + '" onchange="ServiceModeChange(this);" class="servicedisable" >'
    if(each_service.servicemode == 'PDS'):
        tblrows += '<option value="Hours">Hours</option><option value="PDS" selected>PDs</option></select>&nbsp;'
    else:
        tblrows += '<option value="Hours" selected>Hours</option><option value="PDS">PDs</option></select>&nbsp;'
    tblrows += '<input type="button" id="btntotaleffort_' + i + '" value="Get Effort Summary"  title= "Get Effort Summary" onclick="CalcEffortSummary(this);" />'
    tblrows += '</td></tr></table>'
    tblrows += '<div class="scroll">'
    tblrows += '<table style="min-width:850px;" cellpadding="0" cellspacing="0" class="total_budget" id="' + tblid + '" border="1">'
    tblrows += '<thead>'
    tblrows += '<tr><th>Role</th><th>Offshore Hrs</th><th>Offshore PDs</th><th>Onsite Hrs</th><th>Onsite PDs</th><th><b>Total (PDs)</b></th</tr>'
    tblrows += '</thead>'
    tblrows += '<tbody>'
    tblrows += '</tbody>'
    tblrows += '<tfoot>'
    tblrows += '</tfoot>'
    tblrows += '</table>'
    tblrows += '</div><br>'
    return tblrows


def fill_editmode_phase_details(id, i):
    tblrows = ''
    phase_type_details = OIRequestPhaseEffort.objects.filter(oi_request_service__oi_request__id=id, oi_request_service__service__id=i).order_by('phase__code')
    for each in phase_type_details:
        tblrows += generate_phase_detail(i, each.phase.id, each.phase.name, each)
    return tblrows


def generate_phase_detail(i, phase_id, phase_val, each):
    divid = 'divphasedetail_' + i + '_' + phase_id
    tblrows = '<div id="' + divid + '" class="scroll" >'
    tblrows += generate_phaseinfo(i, phase_id, phase_val, each)
    tblrows += generate_effor_resource(phase_id, phase_val, True, i, each)
    tblrows += generate_effor_resource(phase_id, phase_val, False, i, each)
    tblrows += '</div>'
    return tblrows


def generate_phaseinfo(i, phase_id, phase_val, each):
    phasemode = ProjectMode.objects.all().exclude(id="ProjectMode6").filter(is_active=1).order_by('name')
    fillModePhase = fill_phase_mode(phasemode, each.project_mode.id)
    tblrows = ''
    tblrows += '<br><div class="scroll">'
    tblid = 'phaseinfo_' + i + '_' + phase_id
    tblrows += '<table border="1" cellpadding="0" cellspacing="0" style="min-width:850px;" class="total_budget" id=' + tblid + '  >'
    tblrows += '<thead>'
    tblrows += '<tr><td style="text-align:left;"><label style="color:blue;font-size:14px;">Phase Name: ' + phase_val + '</label></td></tr>'
    tblrows += '<tr><th>Project Mode&nbsp;<select id="project_mode_' + i + '_' + phase_id + '" name="project_mode_' + i + '_' + phase_id + '" class="servicedisable" onchange="verifyservicemode(this);" ><option value="">--select--</option>'
    tblrows += fillModePhase
    tblrows += '</select>'
    tblrows += '&nbsp;Start Date&nbsp;<input type="text" id="start_date_' + i + '_' + phase_id + '" name="start_date_' + i + '_' + phase_id + '" class="start_date_class disableamend" value="' + getdatetodisplay(each.phase_start_date) + '" />'
    tblrows += '&nbsp;End Date&nbsp;<input type="text"  id="end_date_' + i + '_' + phase_id + '" name="end_date_' + i + '_' + phase_id + '" class="end_date_class" value="' + getdatetodisplay(each.phase_end_date) + '" />'
    tblrows += '&nbsp;&nbsp;% of Total Effort&nbsp;<input type="text" id="per_total_effort_' + i + '_' + phase_id + '" name="per_total_effort_' + i + '_' + phase_id + '"  value ="0"  readonly="readonly" />'
    tblrows += '<input type="hidden" id="noofmonts_' + i + '_' + phase_id + '" name="noofmonts_' + i + '_' + phase_id + '" />'
    tblrows += '<div>Remarks&nbsp;<textarea name="remarks_'+i+'_'+phase_id+'" id="remarks_'+i+'_'+phase_id+'"  style="width:92%;">'+ each.remarks +'</textarea></div>'
    tblrows += '</th>'
    tblrows += '</tr></thead>'
    tblrows += '</table>'
    tblrows += '</div>'
    return tblrows


def generate_effor_resource(phase_id, phase_val, is_resource, i, each):
    tblrows = ''
    tblid = 'budgeteffort_' + i + '_' + phase_id
    tblid = tblid + '_resource' if(is_resource) else tblid + '_tool'
    tblrows += '<br><div class="scroll">'
    tblrows += '<table border="1" cellpadding="0" cellspacing="0" style="min-width:850px;" class="total_budget" id=' + tblid + '  >'
    tblrows += '<thead>'
    tblrows += generate_resource(phase_id, is_resource, i, each)
    tblrows += '</thead>'
    tblrows += '<tbody>'
    tblrows += fill_phase_effort_detail(phase_id, is_resource, i, each)
    tblrows += '</tbody>'
    tblrows += '<tfoot></tfoot>'
    tblrows += '</table>'
    tblrows += '</div>'
    return tblrows


def generate_resource(phase_id, is_resource, i, each):
    role_len = str(len(OIRequestPhaseEffortDetail.objects.filter(phase=each, effort_type='Role')))
    tool_len = str(len(OIRequestPhaseEffortDetail.objects.filter(phase=each, effort_type='Tool')))
    tblrows = ''
    month_data = get_header_monthwise(is_resource, False)
    for each_month in Utility().spanning_months(each.phase_start_date, each.phase_end_date):
        month_data += '<th style="text-align:center;font-weight:bold;color:maroon;" colspan="5" >' + datetime.strftime(each_month, "%b %Y") + '</th>'
    month_data += '</tr>'
    if(is_resource):
        tblrows += '<tr><th style="text-align:center;">&nbsp;<img src="/static/css/images/icon_addlink.gif" alt="add" title="Add" class="disablephaseadd" id="addresource_' + i + '_' + phase_id + '"   onclick=\"addrow(this,null,null,null,null,null,null,true);\" /></th>'
        tblrows += '<input type="hidden" id="rolelen_' + i + '_' + phase_id + '" name="rolelen_' + i + '_' + phase_id + '" value="' + role_len + '" />'
    else:
        tblrows += '<tr><th style="text-align:center;">&nbsp;<img src="/static/css/images/icon_addlink.gif" alt="add" title="Add" class="disablephaseadd" id="addtool_' + i + '_' + phase_id + '"   onclick=\"addrow(this,null,null,null,null,null,null,false);\" />'
        tblrows += '<input type="hidden" id="toollen_' + i + '_' + phase_id + '" name="toollen_' + i + '_' + phase_id + '" value="' + tool_len + '" /></th>'
    if(is_resource):
        tblrows += '<th >Role</th>'
    else:
        tblrows += '<th >Tool</th>'
    tblrows += '<th >Location</th>'
    tblrows += '<th >Count</th>'
    tblrows += '<th >Start Date</th>'
    tblrows += '<th >End Date</th>'
    for each_month in Utility().spanning_months(each.phase_start_date, each.phase_end_date):
        tblrows += '<th style="width: 60px;">Workdays</th>'
        tblrows += '<th style="width: 60px;">Offshore Hour(s)</th>'
        tblrows += '<th style="width: 60px;">Offshore PDs</th>'
        tblrows += '<th style="width: 60px;">Onsite Hour(s)</th>'
        tblrows += '<th style="width: 60px;">Onsite PDs</th>'
    tblrows += '</tr>'
    month_data += tblrows
    return month_data


def get_header_monthwise(is_resource, is_totalbudget):
    if(is_totalbudget):
        month_data = '<tr><th colspan="3" style="text-align:center;font-weight:bold;color:maroon;">Total Budget Effort</th>'
    elif(is_resource):
        month_data = '<tr><th></th><th colspan="5" style="text-align:center;font-weight:bold;color:maroon;">Budget Resources</th>'
    else:
        month_data = '<tr><th></th><th colspan="5" style="text-align:center;font-weight:bold;color:maroon;">Budget Tool Utilization</th>'
    return month_data


def fill_phase_effort_detail(phase_id, is_resource, i, each):
    id = each.oi_request_service.oi_request.id
    tblrows = ''
    oi_effort = OIRequestPhaseEffortDetail.objects.filter(phase__oi_request_service__oi_request=id, phase__oi_request_service__service__id=i, phase__phase__id=phase_id)
    if(is_resource):
        oi_effort = oi_effort.filter(effort_type='Role')
    else:
        oi_effort = oi_effort.filter(effort_type='Tool')

    trlength = 1
    for each_effort in oi_effort:
        tblrows += input_resource_data(is_resource, phase_id, i, trlength, each_effort)
        trlength += 1
    return tblrows


def input_resource_data(is_resource, j, i, trlength, each_effort):
    trlength = str(trlength)
    role = Role.objects.complex_filter({'role_type': 'Project', 'is_active': True}).order_by('name')
    country = ResourceSubRegion.objects.all().filter(is_active=1).order_by('name')
    tool = Tools.objects.all().filter(is_active=1).order_by('name')
    roletoolid = each_effort.role.id if(is_resource) else each_effort.tool.id
    fillRole = fill_role(role, roletoolid)
    fillTool = fill_tool(tool, roletoolid)
    fillCountry = fill_country(country, each_effort.location.id)
    control_id = ''
    tblrows = ''
    tblrows += '<tr>'
    tblrows += '<td class="row_odd"><img src="/static/css/images/icon_deletelink.gif" style="cursor:pointer;" alt="delete" class="disableadddel" title="Delete" onclick=\"deleterow(this);\" /></td>'
    tblrows += '<td style="text-align:left" class="row_odd">'
    if is_resource:
        control_id = 'resource'
        tblrows += ' <select id="' + control_id + '_role_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_role_' + i + '_' + j + '_' + trlength + '"><option value="select">--Select--</option>'
        tblrows += fillRole
        tblrows += '</select>'
    else:
        control_id = 'tool'
        tblrows += ' <select id="' + control_id + '_role_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_role_' + i + '_' + j + '_' + trlength + '"><option value="select">--Select--</option>'
        tblrows += fillTool
        tblrows += '</select>'

    tblrows += '</td>'
    tblrows += '<td class="row_odd"><select id="' + control_id + '_location_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_location_' + i + '_' + j + '_' + trlength + '" onchange="WorkdaysCalculation(this)"><option value="">--select--</option>'
    tblrows += fillCountry
    tblrows += '</select></td>'
    tblrows += '<td class="row_odd"><input type="text" maxlength="5" id="' + control_id + '_count_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_count_' + i + '_' + j + '_' + trlength + '" style="width:50px;" value="' + str(each_effort.count) + '" maxlength="4" onblur="return CheckInt(this);" onchange="WorkdaysCalculation(this)" onkeypress = "return CheckIsInt(event,this);" oncontextmenu="return false;"  /></td>'
    tblrows += '<td class="row_odd" style="text-align:left;width:500px;"><input type="text"  class="role_startdate_class" id="' + control_id + '_startdate_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_startdate_' + i + '_' + j + '_' + trlength + '" value="' + getdatetodisplay(each_effort.start_date) + '" style="width:90px;" onchange="WorkdaysCalculation(this)"/></td>'
    tblrows += '<td class="row_odd" style="text-align:left;width:500px;"><input type="text"  class="role_enddate_class" id="' + control_id + '_enddate_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_enddate_' + i + '_' + j + '_' + trlength + '" value="' + getdatetodisplay(each_effort.end_date) + '" style="width:90px;" onchange="WorkdaysCalculation(this)"/></td>'
    oi_monthly_data = OIRequestEffortMonthWiseDetail.objects.filter(effort_detail=each_effort).order_by('month')
    sericemode_val = each_effort.phase.oi_request_service.servicemode
    for k in range(1, len(oi_monthly_data) + 1):
        each_effort_detail = oi_monthly_data[k - 1]
        tblrows += input_month_data(control_id, k, i, j, trlength, sericemode_val, each_effort_detail)
    tblrows += '</tr>'
    return tblrows


def input_month_data(control_id, k, i, j, trlength, sericemode_val, each_effort_detail):
    readonlyhrs = ''
    readonlypds = ''
    if (sericemode_val == 'Hours'):
        readonlypds = ' readonly = "readonly" '
    else:
        readonlyhrs = ' readonly = "readonly" '
    onsite_pds = ''
    offshore_pds = ''
    if(each_effort_detail.effort_detail.location.location_type == 'Offshore'):
        onsite_pds = ' readonly = "readonly" '
    elif(each_effort_detail.effort_detail.location.location_type == 'Onsite'):
        offshore_pds = ' readonly = "readonly" '
    k = str(k)
    tblrows = ''
    tblrows += '<td class="row_odd"><input type="text" id="' + control_id + '_workdays_' + k + '_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_workdays_' + k + '_' + i + '_' + j + '_' + trlength + '"   style="width:50px;" value="' + str(each_effort_detail.workdays) + '" maxlength="5" onblur="return CheckInt(this);" onkeypress = "return CheckIsInt(event,this);" oncontextmenu="return false;"   readonly="readonly"  /></td>'
    tblrows += '<td class="row_odd"><input type="text" id="' + control_id + '_offshorehours_' + k + '_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_offshorehours_' + k + '_' + i + '_' + j + '_' + trlength + '" ' + readonlyhrs + ' ' + offshore_pds + ' style="width:50px;" class="hours"  value="' + str(each_effort_detail.offshore_hours) + '" maxlength="5" onblur="return CheckInt(this);" onchange = "CheckWorkdays(this);" onkeypress = "return CheckIsInt(event,this);" oncontextmenu="return false;" /></td>'
    tblrows += '<td class="row_odd"><input type="text" id="' + control_id + '_offshorepds_' + k + '_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_offshorepds_' + k + '_' + i + '_' + j + '_' + trlength + '" ' + readonlypds + ' ' + offshore_pds + ' style="width:50px;" class="pds" value="' + str(each_effort_detail.offshore_pds) + '" maxlength="5" onblur="return CheckInt(this);" onchange = "CheckWorkdays(this);" onkeypress = "return CheckIsInt(event,this);" oncontextmenu="return false;" /></td>'
    tblrows += '<td class="row_odd"><input type="text" id="' + control_id + '_onsitehours_' + k + '_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_onsitehours_' + k + '_' + i + '_' + j + '_' + trlength + '" ' + readonlyhrs + ' ' + onsite_pds + ' style="width:50px;" class="hours"  value="' + str(each_effort_detail.onsite_hours) + '" maxlength="5" onblur="return CheckInt(this);" onchange = "CheckWorkdays(this);" onkeypress = "return CheckIsInt(event,this);" oncontextmenu="return false;" /></td>'
    tblrows += '<td class="row_odd"><input type="text" id="' + control_id + '_onsitepds_' + k + '_' + i + '_' + j + '_' + trlength + '" name="' + control_id + '_onsitepds_' + k + '_' + i + '_' + j + '_' + trlength + '" ' + readonlypds + ' ' + onsite_pds + ' style="width:50px;" class="pds" value="' + str(each_effort_detail.onsite_pds) + '"  maxlength="5" onblur="return CheckInt(this);" onkeypress = "return CheckIsInt(event,this);" onchange = "CheckWorkdays(this);" oncontextmenu="return false;" /></td>'
    return tblrows


def getdatetodisplay(data):
    data = str(data)
    newdate = ''
    try:
        olddate = datetime.strptime(data, settings.DB_DATE_FORMAT)
        newdate = datetime.strftime(olddate, settings.APP_DATE_FORMAT)
    except:
        return newdate
    return newdate

register.simple_tag(fill_phase)
register.simple_tag(fill_tool)
register.simple_tag(fill_role)
register.simple_tag(fill_mode)
register.simple_tag(fill_phase_mode)
register.simple_tag(fill_country)
register.simple_tag(input_resource_data)
register.simple_tag(input_month_data)
register.simple_tag(fill_editmode_oirequest_details)
register.filter(truncchar)
