from pydantic import BaseModel, Field, EmailStr, SecretStr


class User(BaseModel):
    id: str = Field(..., description="Id of the user", example="1234567890")
    email: EmailStr = Field(..., description="Email of the user", example="joe.doe@email.com")
    password: SecretStr = Field(
        ..., description="Password of the user", example="supersecret@#password"
    )
    first_name: str = Field(..., description="First name of the user", example="Joe")
    last_name: str = Field(..., description="Last name of the user", example="Doe")
    two_factor_enabled: bool = Field(
        False, description="Two factor authentication enabled", example=True
    )

    @classmethod
    def from_db(cls, row) -> "User":
        return cls(
            id=str(row["id"]),
            email=row["email"],
            password=SecretStr(row["password"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            two_factor_enabled=row["two_factor_enabled"],
        )
