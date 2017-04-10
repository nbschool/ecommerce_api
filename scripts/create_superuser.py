import click
import uuid
from models import User
from utils import non_empty_str


@click.command()
def main():
    click.echo('####################\n####################\nADMIN USER SCRIPT\n')
    click.echo('####################\n####################\n')
    click.echo('Here you can create an admin user. For eachone you have to insert:\n')
    click.echo('first name\n-last name\n-email\n-password')

    first_name = click.prompt('Please enter your first name')
    last_name = click.prompt('Please enter your last name')
    email = click.prompt('Please enter a valid email')
    password = click.prompt('Please enter your password')

    if click.confirm('Do you want to continue and insert the admin user?'):

        required_fields = ['first_name', 'last_name', 'email', 'password']
        request_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        }

        for field in required_fields:
            try:
                value = request_data[field]
                non_empty_str(value, field)
            except (KeyError, ValueError):
                msg = 'ERROR! Some fields are empty or required'
                print(msg)
                return

        # If email is present in the database return a BAD_REQUEST response.
        if User.exists(request_data['email']):
            msg = 'ERROR! email already present'
            print(msg)
            return

        User.create(
            user_id=uuid.uuid4(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=User.hash_password(password),
            admin=True
        )
        print("Great! Insert successfully")
        # for user in User.select():
        #     print(user.json())


if __name__ == '__main__':
    main()
