/** @odoo-module **/

import {AnalyticDistribution} from "@analytic/components/analytic_distribution/analytic_distribution";
import {patch} from "web.utils";
import {onMounted, onWillUnmount, useState} from "@odoo/owl";

patch(AnalyticDistribution.prototype, "custom.analytic_distribution.patch", {
    setup() {
        this._super(...arguments);
        this.relatedAccountIDs = useState([]);
        this.__alive = true;
        onWillUnmount(() => {
            this.__alive = false;
        });
        onMounted(() => {
            this._updateRelatedAccountIDs();
        });
    },

    async onSelect(option, params, tag) {
        await this._super(option, params, tag);
        await this._updateRelatedAccountIDs();
    },

    async deleteTag(id, fromGroup) {
        await this._super(id, fromGroup);
        await this._updateRelatedAccountIDs();
    },

    async _onSearchMore(searchTerm, editedTag) {
        const originalAddDialog = this.addDialog.bind(this);
        this.addDialog = (component, props, options) => {
            if (props && typeof props.onSelected === "function") {
                const originalOnSelected = props.onSelected;
                props.onSelected = async (...args) => {
                    const result = await originalOnSelected(...args);
                    await this._updateRelatedAccountIDs();
                    return result;
                };
            }
            // Restore immediately after intercepting
            this.addDialog = originalAddDialog;
            return originalAddDialog(component, props, options);
        };
        return await this._super(searchTerm, editedTag);
    },

    async _updateRelatedAccountIDs() {
        if (!this.__alive) return;
        if (!this.existingAnalyticAccountIDs.length) {
            this.relatedAccountIDs.splice(0);
            return;
        }
        let relatedIds = [];
        try {
            relatedIds = await this.orm.call(
                "account.analytic.account",
                "get_related_account_ids",
                [this.existingAnalyticAccountIDs]
            );
        } catch (e) {
            if (!this.__alive) return;
            throw e;
        }
        if (!this.__alive) return;
        this.relatedAccountIDs.splice(0);
        this.relatedAccountIDs.push(...(relatedIds || []));
    },

    analyticAccountDomain(groupId = null) {
        const domain = this._super(groupId);
        if (this.relatedAccountIDs.length) {
            domain.push(["id", "in", this.relatedAccountIDs]);
        }
        return domain;
    },
});
