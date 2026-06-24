import os

from pandasai.data_loader.semantic_layer_schema import (
    Column,
    SemanticLayerSchema,
    Source,
    SQLConnectionConfig,
)

_db_config = SQLConnectionConfig(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
)

# ---------------------------------------------------------------------------
# public schema — raw operational tables
# ---------------------------------------------------------------------------

_users = SemanticLayerSchema(
    name="users",
    description="Registered users with signup details, country, and device type. Use for individual user lookups and segmentation by country or device.",
    source=Source(type="postgres", connection=_db_config, table="users"),
    columns=[
        Column(name="user_id", type="integer", description="Unique identifier for the user."),
        Column(name="signup_date", type="datetime", description="Date and time when the user signed up."),
        Column(name="country", type="string", description="User's country based on IP geolocation at signup. Values: US, EU, India, Rest."),
        Column(name="device_type", type="string", description="Device used at signup. Values: iOS, Android, Web."),
    ],
)

_sessions = SemanticLayerSchema(
    name="sessions",
    description="User activity sessions — one row per session with duration and activity type. Use for individual session-level questions. For DAU/WAU/MAU use user_activity_metrics instead.",
    source=Source(type="postgres", connection=_db_config, table="sessions"),
    columns=[
        Column(name="session_id", type="integer", description="Unique identifier for the session."),
        Column(name="user_id", type="integer", description="Foreign key linking to the users table."),
        Column(name="session_date", type="datetime", description="Date and time when the session occurred."),
        Column(name="duration_minutes", type="integer", description="Duration of the session in minutes."),
        Column(name="activity_type", type="string", description="Main activity during the session. Values: browse, listen, read."),
    ],
)

_subscriptions = SemanticLayerSchema(
    name="subscriptions",
    description="User subscription records including plan, status, and lifecycle dates. Use for subscription lifecycle questions: churn, plan distribution, active vs expired counts.",
    source=Source(type="postgres", connection=_db_config, table="subscriptions"),
    columns=[
        Column(name="subscription_id", type="integer", description="Unique identifier for the subscription."),
        Column(name="user_id", type="integer", description="Foreign key linking to the users table."),
        Column(name="plan", type="string", description="Subscription plan. Values: free, monthly, annual."),
        Column(name="start_date", type="datetime", description="Date when the subscription started."),
        Column(name="end_date", type="datetime", description="Date when the subscription ended. Null for currently active subscriptions."),
        Column(name="status", type="string", description="Current subscription status. Values: active, canceled, expired."),
    ],
)

_payments = SemanticLayerSchema(
    name="payments",
    description="Payment transactions linked to subscriptions. Use for individual payment-level questions: method breakdown, payment history per subscription. For total revenue per user use user_revenue_summary instead.",
    source=Source(type="postgres", connection=_db_config, table="payments"),
    columns=[
        Column(name="payment_id", type="integer", description="Unique identifier for the payment."),
        Column(name="subscription_id", type="integer", description="Foreign key linking to the subscriptions table."),
        Column(name="payment_date", type="datetime", description="Date when the payment was made."),
        Column(name="amount_usd", type="float", description="Payment amount in USD. Values: 10.00 (monthly plan), 100.00 (annual plan)."),
        Column(name="method", type="string", description="Payment method used. Values: card, paypal, apple_pay, google_pay."),
    ],
)

# ---------------------------------------------------------------------------
# marts schema — pre-aggregated business metrics
# ---------------------------------------------------------------------------

_user_activity_metrics = SemanticLayerSchema(
    name="user_activity_metrics",
    description="Daily engagement metrics: DAU, WAU, and MAU per calendar date. Use for all DAU/WAU/MAU and engagement trend questions. Do not recompute these from the sessions table.",
    source=Source(type="postgres", connection=_db_config, table="marts.user_activity_metrics"),
    columns=[
        Column(name="date", type="date", description="Calendar date associated with the metric. Each row represents one day of activity."),
        Column(name="dau", type="integer", description="Daily Active Users: distinct users with at least one session on this exact date."),
        Column(name="wau", type="integer", description="Weekly Active Users: distinct users with at least one session in the 7-day period ending on this date."),
        Column(name="mau", type="integer", description="Monthly Active Users: distinct users with at least one session in the 30-day period ending on this date. Used to calculate DAU/MAU stickiness ratios."),
    ],
)

_user_revenue_summary = SemanticLayerSchema(
    name="user_revenue_summary",
    description="Per-user revenue summary with lifetime value and most recent subscription plan. Use for revenue aggregations: top customers, total revenue by country or plan. Do not join users and payments manually for these questions.",
    source=Source(type="postgres", connection=_db_config, table="marts.user_revenue_summary"),
    columns=[
        Column(name="user_id", type="integer", description="Unique identifier for the user."),
        Column(name="country", type="string", description="User country at signup."),
        Column(name="signup_date", type="datetime", description="Date the user signed up."),
        Column(name="plan", type="string", description="Most recent subscription plan. Values: free, monthly, annual."),
        Column(name="total_payments", type="integer", description="Total number of payments made by the user."),
        Column(name="total_revenue_usd", type="float", description="Total revenue generated by the user in USD."),
        Column(name="last_payment_date", type="datetime", description="Most recent payment date for the user."),
    ],
)

# The engine imports this list — add new schemas here.
SCHEMAS: list[SemanticLayerSchema] = [
    _users,
    _sessions,
    _subscriptions,
    _payments,
    _user_activity_metrics,
    _user_revenue_summary,
]
