from auth.password_utils import hash_password
from database.models import UserModel

created = 0

for i in range(1, 51):

    username = f"dr_{i:03d}"
    email = f"dr_{i:03d}@medchain.com"

    if UserModel.get_by_username(username):
        print(f"{username} already exists")
        continue

    user_id = UserModel.create(
        username=username,
        email=email,
        password_hash=hash_password("Doctor@1234"),
        role="doctor"
    )

    if user_id:
        created += 1
        print(f"Created {username}")

print()
print(f"Total doctors created: {created}")