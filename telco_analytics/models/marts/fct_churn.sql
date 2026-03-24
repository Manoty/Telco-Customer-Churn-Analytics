with enriched as (

    select * from {{ ref('int_customers_enriched') }}

),

final as (

    select
        -- Primary key
        customer_id,

        -- Target
        has_churned,

        -- Churn risk dimensions
        contract_type,
        tenure_months,
        tenure_bucket,
        tenure_bucket_order,
        monthly_charges,
        monthly_charge_tier,
        lifetime_value,
        addon_service_count,
        is_high_value,
        internet_service_type,
        payment_method,

        -- Service flags most correlated with churn
        has_online_security,
        has_tech_support,
        has_online_backup,
        has_device_protection,

        -- Demographics
        is_senior_citizen,
        has_partner,
        has_dependents

    from enriched

)

select * from final