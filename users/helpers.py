import uuid
from os.path import splitext


def upload_to_user_cover_directory(user_profile, filename):
    creator = user_profile.creator
    return _upload_to_user_directory(creator=creator, filename=filename)

def _upload_to_user_directory(creator, filename):
    extension = splitext(filename)[1].lower()
    new_filename = str(uuid.uuid4()) + extension

    path = 'users/%(user_uuid)s/' % {
        'user_uuid': str(creator.id)}

    return '%(path)s%(new_filename)s' % {'path': path,
                                         'new_filename': new_filename, }
