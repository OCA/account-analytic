import logging

_logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal
def migrate(cr, installed_version):
    _logger.info(f'Start migration stock_analytic 17.0.0.0.0 from {installed_version} - pre cleanup')

    with cr.savepoint():
        cr.execute(
            """
                delete from ir_ui_view where arch_fs ~ 'stock_analytic'           
            """
        )

        cr.execute(
            """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='stock_move' and column_name='analytic_distribution'    
            """
        )

        if not cr.fetchone():
            cr.execute(
                """
                    ALTER TABLE stock_move ADD analytic_distribution JSONB NULL;
                    COMMENT ON COLUMN stock_move.analytic_distribution IS 'Analytic Distribution'                
                """
            )

        cr.execute(
            """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='stock_move_line' and column_name='analytic_distribution'    
            """
        )

        if not cr.fetchone():
            cr.execute(
                """                
                    ALTER TABLE stock_move_line ADD analytic_distribution jsonb NULL;
                    COMMENT ON COLUMN stock_move_line.analytic_distribution IS 'Analytic Distribution'              
                """
            )

        cr.execute(
            """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='stock_move' and column_name='analytic_account_id'    
            """
        )

        if cr.fetchone():
            cr.execute(
                """
                    with _analytic_tags as (
                        select stock_move_id, string_agg(distinct distribution, ', ') as distributions
                        from (
                            select aatsmr.stock_move_id,  aaa.id, aat.name, coalesce('"' || aaa.id || '": 100','') as distribution
                            from account_analytic_tag_stock_move_rel aatsmr 
                            left join account_analytic_tag aat on aat.id = aatsmr.account_analytic_tag_id
                            left join account_analytic_account aaa on aaa.code = aat.name and aaa.active 
                        ) x 
                        group by stock_move_id
                    ),
                    _update_query as (
                        select sm.id, 
                        ('{"' || analytic_account_id || '": 100' || case when coalesce(at.distributions,'') =  '' then '' else ', ' || at.distributions end || '}')::jsonb as analytic_distribution
                        from stock_move sm 
                        left join _analytic_tags at on at.stock_move_id = sm.id
                        where analytic_account_id is not null
                    )
                    UPDATE stock_move sm
                    set analytic_distribution = uq.analytic_distribution
                    from _update_query uq
                    where sm.id = uq.id
                """
            )

        cr.execute(
            """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='stock_move_line' AND column_name='analytic_account_id'    
            """
        )

        if cr.fetchone():
            cr.execute(
                """
                    UPDATE stock_move_line
                    SET analytic_distribution = ('{"' || analytic_account_id || '": 100' || '}')::JSONB
                    WHERE analytic_account_id IS NOT NULL
                """
            )

    _logger.info('migration stock_analytic finished')
