insert_user = """
insert into users (email, password, first_name, last_name, two_factor_enabled)
    values (:email, :password, :first_name, :last_name, :two_factor_enabled)
returning id
"""
