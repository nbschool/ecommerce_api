import click
import uuid
from models import User
from utils import non_empty_str


@click.command()
@click.option('--first_name')
@click.option('--last_name')
@click.option('--email')
@click.option('--password')
def main(first_name, last_name, email, password):
    click.echo('####################\n####################\nADMIN USER SCRIPT\n')
    click.echo('####################\n####################\n')
    click.echo('Here you can create an admin user. For eachone you have to insert:\n')
    click.echo('first name\n-last name\n-email\n-password')

    if not first_name:
        first_name = click.prompt('Please enter your first name')
    if not last_name:
        last_name = click.prompt('Please enter your last name')
    if not email:
        email = click.prompt('Please enter a valid email')
    if not password:
        password = click.prompt('Please enter your password')

    request_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password
    }

    for field in request_data:
        try:
            value = request_data[field]
            non_empty_str(value, field)
        except ValueError:
            print('ERROR! Some fields are empty or required')
            return

    # If email is present in the database return a ERROR and close the program.
    if User.exists(request_data['email']):
        print('ERROR! email already present')
        return

    User.create(
        uuid=uuid.uuid4(),
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=User.hash_password(password),
        admin=True
    )
    print("Great! Insert successfully")


if __name__ == '__main__':
    main()
