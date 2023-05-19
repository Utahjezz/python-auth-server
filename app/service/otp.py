import logging
from abc import ABC, abstractmethod


class OTPSenderService(ABC):
    @abstractmethod
    def send_otp(self, email: str, otp: str) -> None:
        pass


class LogOTPSenderService(OTPSenderService):
    def send_otp(self, email: str, otp: str) -> None:
        logging.info(f"Sending OTP {otp} to {email}")
