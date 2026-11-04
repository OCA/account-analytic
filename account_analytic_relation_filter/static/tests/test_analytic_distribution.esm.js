/** @odoo-module **/
/* global QUnit */

QUnit.module("Analytic Distribution Filter - logic only", () => {
    QUnit.test(
        "onSelect and deleteTag update relatedAccountIDs correctly",
        async (assert) => {
            assert.expect(2);

            const fakeComponent = {
                orm: {
                    async call(model, method, args) {
                        if (
                            model === "account.analytic.account" &&
                            method === "get_related_account_ids"
                        ) {
                            if (args[0][0] === 1) {
                                return [2, 3];
                            }
                            return [4, 5];
                        }
                        return [];
                    },
                },
                relatedAccountIDs: [],

                async onSelect() {
                    const relatedIds = await this.orm.call(
                        "account.analytic.account",
                        "get_related_account_ids",
                        [this.existingAnalyticAccountIDs]
                    );
                    this.relatedAccountIDs.splice(0);
                    this.relatedAccountIDs.push(...relatedIds);
                },

                async deleteTag() {
                    if (!this.existingAnalyticAccountIDs.length) {
                        this.relatedAccountIDs.splice(0);
                        return;
                    }
                    const relatedIds = await this.orm.call(
                        "account.analytic.account",
                        "get_related_account_ids",
                        [this.existingAnalyticAccountIDs]
                    );
                    this.relatedAccountIDs.splice(0);
                    this.relatedAccountIDs.push(...relatedIds);
                },

                analyticAccountDomain() {
                    const domain = [];
                    if (this.relatedAccountIDs.length) {
                        domain.push(["id", "in", this.relatedAccountIDs]);
                    }
                    return domain;
                },
            };
            fakeComponent.existingAnalyticAccountIDs = [1];
            await fakeComponent.onSelect();
            assert.deepEqual(fakeComponent.analyticAccountDomain(), [
                ["id", "in", [2, 3]],
            ]);

            fakeComponent.existingAnalyticAccountIDs = [2];
            await fakeComponent.deleteTag();
            assert.deepEqual(fakeComponent.relatedAccountIDs, [4, 5]);
        }
    );
});
