# financial_states.py
"""Financial State Enumerations.

Defines the core state machines and categorical constants for financial operations
within the platform. These enumerations ensure type safety, consistency, and 
database compatibility for transactions, investments, and wallet operations 
across the investment lifecycle.
"""

from enum import StrEnum, auto


class TransactionStatus(StrEnum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    REVERSED = auto()
    EXPIRED = auto()


class DepositStatus(StrEnum):
    PENDING = auto()
    AWAITING_VERIFICATION = auto()
    APPROVED = auto()
    REJECTED = auto()
    FAILED = auto()
    CANCELLED = auto()


class WithdrawalStatus(StrEnum):
    PENDING = auto()
    APPROVED = auto()
    PROCESSING = auto()
    PAID = auto()
    FAILED = auto()
    CANCELLED = auto()


class InvestmentStatus(StrEnum):
    DRAFT = auto()
    ACTIVE = auto()
    MATURED = auto()
    COMPLETED = auto()
    CANCELLED = auto()
    EXPIRED = auto()


class InvestmentPlanStatus(StrEnum):
    ACTIVE = auto()
    ARCHIVED = auto()
    MAINTENANCE = auto()


class DailyIncomeStatus(StrEnum):
    PENDING = auto()
    GENERATED = auto()
    PAID = auto()
    SKIPPED = auto()


class ReferralRewardStatus(StrEnum):
    PENDING = auto()
    PAID = auto()
    CANCELLED = auto()


class GiftCodeStatus(StrEnum):
    ACTIVE = auto()
    REDEEMED = auto()
    EXPIRED = auto()
    DISABLED = auto()


class PaymentMethod(StrEnum):
    PAYSTACK = auto()
    FLUTTERWAVE = auto()
    BANK_TRANSFER = auto()
    CRYPTO = auto()
    WALLET_BALANCE = auto()


class WalletType(StrEnum):
    MAIN = auto()
    INVESTMENT = auto()
    REFERRAL = auto()


class WalletTransactionType(StrEnum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    INVESTMENT = auto()
    EARNING = auto()
    REWARD = auto()
    ADJUSTMENT = auto()


class WalletTransactionReason(StrEnum):
    DEPOSIT_CONFIRMED = auto()
    WITHDRAWAL_REQUEST = auto()
    INVESTMENT_PLACEMENT = auto()
    DAILY_ROI = auto()
    REFERRAL_BONUS = auto()
    ADMIN_ADJUSTMENT = auto()


class NotificationStatus(StrEnum):
    UNREAD = auto()
    READ = auto()
    ARCHIVED = auto()


class AnnouncementStatus(StrEnum):
    DRAFT = auto()
    PUBLISHED = auto()
    EXPIRED = auto()


class SupportTicketStatus(StrEnum):
    OPEN = auto()
    IN_PROGRESS = auto()
    PENDING_USER = auto()
    CLOSED = auto()
    RESOLVED = auto()


class SupportTicketPriority(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    URGENT = auto()


class SupportTicketCategory(StrEnum):
    ACCOUNT = auto()
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    INVESTMENT = auto()
    TECHNICAL = auto()
    OTHER = auto()
