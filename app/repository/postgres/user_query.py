insert_user = """
insert into users (email, password, first_name, last_name, two_factor_enabled)
    values (:email, :password, :first_name, :last_name, :two_factor_enabled)
returning id
"""

get_user_by_email = """
select id, email, password, first_name, last_name, two_factor_enabled
    from users
    where email = :email
"""
