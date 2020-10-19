import os
from datetime import datetime

from docx import Document

from clubs_and_events.settings import STORAGE_BASE_DIR
from membership.models import Membership


def generate_docx(file_name, generated_file_name=None, club=None, advisor=None, objective=str(), objective_list=tuple(),
                  room=str(), schedule=str(), plan_list=tuple(), merit=str(), save=False):
    # Init Document
    document = Document('generator/docx/{}'.format(file_name))

    # Init Generated File Name
    if generated_file_name is None:
        generated_file_name = 'generated-' + file_name

    # Init Generated Document Directories
    base_path = '{}/generated_docx'.format(STORAGE_BASE_DIR)
    id_path = '{}/{}'.format(base_path, club.id)
    path = '{}/{}'.format(id_path, generated_file_name)

    # Create Directories if not present
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if not os.path.exists(id_path):
        os.mkdir(id_path)

    # Storing Data
    data = {
        'date': get_date(),
        'club_name': club.name_th.replace('ชุมนุม', ''),
        'student_committee_president': '',
        'president': get_club_president(club),
        'advisor': advisor.name,
        'staff_list': get_staff_list(club),
        'objective': objective,
        'objective_list': objective_list,
        'room': room,
        'schedule': schedule,
        'plan_list': plan_list,
        'merit': merit,
        'member_list': get_member_list(club)
    }

    # Formatting Data
    data['objective_list'] = data['objective_list'].split('\n') # Always a list
    data['plan_list'] = data['plan_list'].split('\n')           # Always a list

    for i in ('schedule', 'merit'):
        if '\n' in data[i]:
            data[i] = data[i].split('\n') # Able to be a list
        else:
            data[i] = '\t' + data[i]      # Not a list, add a tab

    # Replace Paragraphs
    for paragraph in document.paragraphs:
        for inline in paragraph.runs:
            for j in data:
                if not isinstance(data[j], list):
                    inline.text = inline.text.replace('{%s}' % j, data[j])
                else:
                    inline.text = inline.text.replace(
                        '{%s}' % j,
                        '\n'.join(['\t{}. {}'.format(
                            i + 1, data[j][i].replace('\n', '').replace('\r', '')
                        ) for i in range(len(data[j]))])
                    )

    # Replace Paragraphs in Tables
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for inline in paragraph.runs:
                        for j in data:
                            if not isinstance(data[j], list):
                                inline.text = inline.text.replace('{%s}' % j, data[j])

    # Document Saving
    if save:
        document.save(path)

    # Return
    return document


def get_date():
    today = datetime.now().date()
    months = {
        1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน', 5: 'พฤษภาคม', 6: 'มิถุนายน',
        7: 'กรกฎาคม', 8: 'สิงหาคม', 9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม',
    }

    return '{} {} {}'.format(today.day, months[today.month], today.year + 543)


def get_club_president(club):
    membership = Membership.objects.get(community_id=club.id, position=3, status='A')

    return membership.user.name


def get_staff_list(club):
    memberships = Membership.objects.filter(
        community_id=club.id, position__in=(1, 2, 3), status='A'
    ).order_by('-position')

    staff_list = list()

    for i in memberships:
        if i.position == 3:
            staff_list.append('{}\tรหัสนักศึกษา {}\tประธานชุมนุม'.format(i.user.name, i.user.username.replace('it', '')))
        elif i.position == 2:
            staff_list.append('{}\tรหัสนักศึกษา {}\tรองประธานชุมนุม'.format(i.user.name, i.user.username.replace('it', '')))
        elif i.position == 1:
            staff_list.append('{}\tรหัสนักศึกษา {}\tกรรมการ'.format(i.user.name, i.user.username.replace('it', '')))

    return staff_list


def get_member_list(club):
    memberships = Membership.objects.filter(community_id=club.id, status='A').order_by('-position')

    return [i.user.name for i in memberships]
