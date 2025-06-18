# Copyright 2025 Bernat Obrador APSL-Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockAnalyticModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        cls.stock_location = cls.env["stock.location"].create({"name": "Test Location"})
        cls.stock_location_2 = cls.env["stock.location"].create(
            {"name": "Test Location 2"}
        )
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "avg_price": 100.0,
                "avg_weight": 20.0,
                "supplement": 5.0,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
                "plan_id": cls.analytic_plan.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.analytic_account_negative = cls.env["account.analytic.account"].create(
            {
                "name": "Test Negative Account",
                "plan_id": cls.analytic_plan.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.outgoing_picking_type = cls.env.ref("stock.picking_type_out")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "categ_id": cls.product_category.id,
                "list_price": 100.0,
                "type": "product",
            }
        )

        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Test Tax 10%",
                "amount": 10.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "company_id": cls.env.company.id,
            }
        )

        cls.stock_analytic_rule = cls.env["stock.analytic.rule"].create(
            {
                "name": "Test Stock Analytic Rule",
                "location_from_ids": [(6, 0, [cls.stock_location.id])],
                "location_dest_ids": [(6, 0, [cls.stock_location_2.id])],
                "analytic_distribution": {str(cls.analytic_account.id): 100},
                "analytic_distribution_negative": {
                    str(cls.analytic_account_negative.id): 100
                },
                "amount_compute_type": "category",
            }
        )

        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "quantity": 100.0,
            }
        )

    def _get_amount(self, category, quantity):
        return (category.avg_price * (category.avg_weight * quantity)) + (
            (category.avg_weight * quantity) * category.supplement
        )

    def test_compute_type_product_with_taxes(self):
        """Test the compute amount when using product price and taxes."""
        self.stock_analytic_rule.amount_compute_type = "product"
        self.stock_analytic_rule.include_taxes = True
        self.product.taxes_id = [(6, 0, [self.tax.id])]
        product = self.product
        amount = self.stock_analytic_rule._compute_amount(product, 5.0)
        taxes = product.taxes_id.filtered(lambda t: t.company_id == self.env.company)
        price_unit = product.lst_price
        tax_result = taxes.compute_all(price_unit, quantity=5.0, product=product)

        expected_amount = tax_result["total_included"]
        self.assertEqual(
            amount, expected_amount, "Amount should be based on product list price"
        )

    def test_compute_type_product_without_taxes(self):
        self.stock_analytic_rule.amount_compute_type = "product"
        self.stock_analytic_rule.include_taxes = False
        product = self.product
        amount = self.stock_analytic_rule._compute_amount(product, 5.0)
        expected_amount = product.lst_price * 5.0

        self.assertEqual(
            amount, expected_amount, "Amount should be based on products price"
        )

    def test_stock_move_create(self):
        """Test the creation of stock move generates analytic lines"""
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 10.0,
                "quantity": 10.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location_2.id,
                "state": "done",
                "company_id": self.env.company.id,
            }
        )

        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move.id)]
        )

        self.assertTrue(
            analytic_lines, "No analytic lines were created for the stock move"
        )
        self.assertEqual(
            len(analytic_lines),
            2,
            "There should be 2 analytic lines created (positive and negative)",
        )

        expected_positive_amount = self._get_amount(self.product_category, 10.0)
        expected_negative_amount = -expected_positive_amount

        positive_line = analytic_lines.filtered(lambda line: line.amount > 0)
        negative_line = analytic_lines.filtered(lambda line: line.amount < 0)

        self.assertEqual(
            positive_line.amount,
            expected_positive_amount,
            "Positive amount is not calculated correctly",
        )
        self.assertEqual(
            negative_line.amount,
            expected_negative_amount,
            "Negative amount is not calculated correctly",
        )
        self.assertEqual(
            positive_line[self.analytic_plan._column_name()].id,
            self.analytic_account.id,
        )
        self.assertEqual(
            negative_line[self.analytic_plan._column_name()].id,
            self.analytic_account_negative.id,
        )

    def test_stock_move_write(self):
        """Test updating a move regenerates analytic lines"""

        move = self.env["stock.move"].create(
            {
                "name": "Test Move Draft",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 5.0,
                "quantity": 5.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location_2.id,
                "state": "draft",
                "company_id": self.env.company.id,
            }
        )

        # Check that no analytic lines were created yet
        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move.id)]
        )
        self.assertFalse(
            analytic_lines, "Analytic lines should not be created for draft moves"
        )

        # Mark the move as done
        move.write({"state": "done"})

        # Check that analytic lines were created
        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move.id)]
        )
        self.assertTrue(
            analytic_lines,
            "Analytic lines were created after updating the move state",
        )
        self.assertEqual(
            len(analytic_lines),
            2,
            "There should be 2 analytic lines created after updating",
        )

        move.write({"quantity": 8.0})

        updated_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move.id)]
        )

        expected_positive_amount = self._get_amount(self.product_category, 8.0)
        expected_negative_amount = -expected_positive_amount

        positive_line = updated_lines.filtered(lambda line: line.amount > 0)
        negative_line = updated_lines.filtered(lambda line: line.amount < 0)

        self.assertEqual(
            positive_line.amount,
            expected_positive_amount,
            "Updated positive amount is calculated correctly",
        )
        self.assertEqual(
            negative_line.amount,
            expected_negative_amount,
            "Updated negative amount is calculated correctly",
        )

    def test_reversal_model(self):
        """Test that the reversal model generates the opposite analytic lines"""
        move = self.env["stock.move"].create(
            {
                "name": "Test reversal Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 7.0,
                "quantity": 7.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location_2.id,
                "state": "done",
                "company_id": self.env.company.id,
            }
        )

        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move.id)]
        )

        self.assertTrue(
            analytic_lines, "No analytic lines were created for the reversal move"
        )
        self.assertEqual(
            len(analytic_lines),
            2,
            "There should be 2 analytic lines created (positive and negative)",
        )

        expected_positive_amount = self._get_amount(self.product_category, 7.0)
        expected_negative_amount = -expected_positive_amount

        positive_line = analytic_lines.filtered(lambda line: line.amount > 0)
        negative_line = analytic_lines.filtered(lambda line: line.amount < 0)

        self.assertEqual(
            positive_line.amount,
            expected_positive_amount,
            "reversal positive amount is not calculated correctly",
        )
        self.assertEqual(
            negative_line.amount,
            expected_negative_amount,
            "reversal negative amount is not calculated correctly",
        )
        self.assertEqual(
            positive_line[self.analytic_plan._column_name()].id,
            self.analytic_account.id,
        )
        self.assertEqual(
            negative_line[self.analytic_plan._column_name()].id,
            self.analytic_account_negative.id,
        )

        # Create reversal move
        reversal_move = self.env["stock.move"].create(
            {
                "name": "Test reversal Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 7.0,
                "quantity": 7.0,
                "location_id": self.stock_location_2.id,
                "location_dest_id": self.stock_location.id,
                "state": "done",
                "company_id": self.env.company.id,
            }
        )

        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", reversal_move.id)]
        )

        self.assertTrue(
            analytic_lines, "Analytic lines were created for the reversal move"
        )
        self.assertEqual(
            len(analytic_lines),
            2,
            "There should be 2 analytic lines created (positive and negative)",
        )

        positive_line = analytic_lines.filtered(lambda line: line.amount > 0)
        negative_line = analytic_lines.filtered(lambda line: line.amount < 0)

        # For reversal, the accounts should be flipped
        self.assertEqual(
            positive_line.amount,
            expected_positive_amount,
            "reversal positive amount is calculated correctly",
        )
        self.assertEqual(
            negative_line.amount,
            expected_negative_amount,
            "reversal negative amount is calculated correctly",
        )
        self.assertEqual(
            positive_line[self.analytic_plan._column_name()].id,
            self.analytic_account_negative.id,
        )
        self.assertEqual(
            negative_line[self.analytic_plan._column_name()].id,
            self.analytic_account.id,
        )

        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "in", (reversal_move.id, move.id))]
        )

        total_amount = sum(line.amount for line in analytic_lines)
        self.assertEqual(
            total_amount, 0.0, "Total amount should be zero after all moves"
        )

    def test_unique_combination_constraint(self):
        """Test that the unique combination constraint works"""
        # Try to create a rule with the same combination
        with self.assertRaises(ValidationError):
            self.env["stock.analytic.rule"].create(
                {
                    "name": "Duplicate Model",
                    "location_from_ids": [(6, 0, [self.stock_location.id])],
                    "location_dest_ids": [(6, 0, [self.stock_location_2.id])],
                }
            )

        # Test copy function bypasses the constraint
        copied_model = self.stock_analytic_rule.copy()
        self.assertEqual(copied_model.name, f"{self.stock_analytic_rule.name} (copy)")

    def test_validation_checks(self):
        """Test validation checks for category weight and price"""

        zero_weight_category = self.env["product.category"].create(
            {
                "name": "Zero Weight Category",
                "avg_weight": 0.0,
                "avg_price": 100.0,
            }
        )

        zero_price_category = self.env["product.category"].create(
            {
                "name": "Zero Price Category",
                "avg_price": 0.0,
                "avg_weight": 20.0,
            }
        )

        product_1 = self.env["product.product"].create(
            {
                "name": "Zero AVG Weight Product",
                "categ_id": zero_weight_category.id,
                "list_price": 100.0,
                "type": "product",
            }
        )

        product_2 = self.env["product.product"].create(
            {
                "name": "Zero AVG Price Product",
                "categ_id": zero_price_category.id,
                "list_price": 100.0,
                "type": "product",
            }
        )

        with self.assertRaises(ValidationError):
            self.env["stock.move"].create(
                {
                    "name": "Zero Weight Move",
                    "product_id": product_1.id,
                    "product_uom": product_1.uom_id.id,
                    "product_uom_qty": 5.0,
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.stock_location_2.id,
                    "state": "done",
                }
            )

        with self.assertRaises(ValidationError):
            self.env["stock.move"].create(
                {
                    "name": "Zero Price Move",
                    "product_id": product_2.id,
                    "product_uom": product_2.uom_id.id,
                    "product_uom_qty": 5.0,
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.stock_location_2.id,
                    "state": "done",
                }
            )

    def test_partial_analytic_distribution(self):
        """Test creation of analytic lines with partial distribution"""

        partial_category = self.env["product.category"].create(
            {
                "name": "Partial Category",
                "avg_price": 50.0,
                "avg_weight": 10.0,
                "supplement": 3.0,
            }
        )
        new_location = self.env["stock.location"].create({"name": "New Location"})
        new_location_2 = self.env["stock.location"].create({"name": "New Location 2"})

        self.env["stock.analytic.rule"].create(
            {
                "name": "Partial Distribution Rule",
                "location_from_ids": [(6, 0, [new_location.id])],
                "location_dest_ids": [(6, 0, [new_location_2.id])],
                "analytic_distribution": {
                    f"""{self.analytic_account.id},
                    {self.analytic_account_negative.id}""": 70,
                    str(self.analytic_account_negative.id): 30,
                },
                "analytic_distribution_negative": {
                    str(self.analytic_account_negative.id): 100
                },
            }
        )

        partial_product = self.env["product.product"].create(
            {
                "name": "Partial Product",
                "categ_id": partial_category.id,
                "list_price": 50.0,
                "type": "product",
            }
        )

        self.env["stock.quant"].create(
            {
                "product_id": partial_product.id,
                "location_id": new_location.id,
                "quantity": 100.0,
            }
        )

        move = self.env["stock.move"].create(
            {
                "name": "Partial Distribution Move",
                "product_id": partial_product.id,
                "product_uom": partial_product.uom_id.id,
                "product_uom_qty": 5.0,
                "quantity": 5.0,
                "location_id": new_location.id,
                "location_dest_id": new_location_2.id,
                "state": "done",
                "company_id": self.env.company.id,
            }
        )

        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move.id)]
        )

        self.assertEqual(
            len(analytic_lines),
            3,
            """Should create 3 analytic lines
            (2 positive and 1 with partial distribution, 1 negative)""",
        )

        total_amount = self._get_amount(partial_category, 5.0)

        positive_lines = analytic_lines.filtered(lambda line: line.amount > 0)
        negative_lines = analytic_lines.filtered(lambda line: line.amount < 0)

        # Check positive lines (split 70/30)
        self.assertEqual(
            len(positive_lines), 2, "Should have 2 positive analytic lines"
        )
        self.assertEqual(
            round(sum(line.amount for line in positive_lines), 2),
            round(total_amount, 2),
            "Sum of positive amounts should equal total amount",
        )

        self.assertEqual(len(negative_lines), 1, "Should have 1 negative analytic line")
        self.assertEqual(
            round(negative_lines[0].amount, 2),
            round(-total_amount, 2),
            "Negative amount should equal total amount with opposite sign",
        )

    def test_no_matching_locations(self):
        """Test no analytic lines created when locations don't match"""

        new_location_1 = self.env["stock.location"].create({"name": "New Location 1"})
        new_location_2 = self.env["stock.location"].create({"name": "New Location 2"})

        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": new_location_1.id,
                "quantity": 20.0,
            }
        )

        move = self.env["stock.move"].create(
            {
                "name": "Unmatched Locations Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 5.0,
                "quantity": 5.0,
                "location_id": new_location_1.id,
                "location_dest_id": new_location_2.id,
                "state": "done",
                "company_id": self.env.company.id,
            }
        )

        analytic_lines = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move.id)]
        )

        self.assertFalse(
            analytic_lines,
            "No analytic lines should be created for unmatched locations",
        )

    def test_multiple_analytic_models(self):
        """Test correct rule selection with multiple rules"""

        new_category = self.env["product.category"].create(
            {
                "name": "New Category",
                "avg_price": 120.0,
                "avg_weight": 25.0,
                "supplement": 10.0,
            }
        )

        new_product = self.env["product.product"].create(
            {
                "name": "New Product",
                "categ_id": new_category.id,
                "list_price": 120.0,
                "type": "product",
            }
        )

        new_location = self.env["stock.location"].create({"name": "New Location"})
        new_location_2 = self.env["stock.location"].create({"name": "New Location 2"})

        self.env["stock.analytic.rule"].create(
            {
                "name": "New Category Rule",
                "location_from_ids": [(6, 0, [new_location.id])],
                "location_dest_ids": [(6, 0, [new_location_2.id])],
                "analytic_distribution": {str(self.analytic_account.id): 100},
                "analytic_distribution_negative": {
                    str(self.analytic_account_negative.id): 100
                },
            }
        )

        self.env["stock.quant"].create(
            {
                "product_id": new_product.id,
                "location_id": new_location.id,
                "quantity": 30.0,
            }
        )

        move1 = self.env["stock.move"].create(
            {
                "name": "Original Product Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 4.0,
                "quantity": 4.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.stock_location_2.id,
                "state": "done",
                "company_id": self.env.company.id,
            }
        )

        move2 = self.env["stock.move"].create(
            {
                "name": "New Product Move",
                "product_id": new_product.id,
                "product_uom": new_product.uom_id.id,
                "product_uom_qty": 3.0,
                "quantity": 3.0,
                "location_id": new_location.id,
                "location_dest_id": new_location_2.id,
                "state": "done",
                "company_id": self.env.company.id,
            }
        )

        # Check analytic lines for the first move
        analytic_lines1 = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move1.id)]
        )

        expected_amount1 = self._get_amount(self.product_category, 4.0)

        # Check analytic lines for the second move
        analytic_lines2 = self.env["account.analytic.line"].search(
            [("stock_move_id", "=", move2.id)]
        )

        expected_amount2 = self._get_amount(new_category, 3.0)

        # Verify correct rule was used for each move
        self.assertEqual(
            round(analytic_lines1.filtered(lambda line: line.amount > 0)[0].amount, 2),
            round(expected_amount1, 2),
            "First move should use original rule supplement",
        )
        self.assertEqual(
            round(analytic_lines2.filtered(lambda line: line.amount > 0)[0].amount, 2),
            round(expected_amount2, 2),
            "Second move should use new rule supplement",
        )
