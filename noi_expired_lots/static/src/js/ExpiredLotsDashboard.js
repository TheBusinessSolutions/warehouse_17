/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { Component, useState, onWillUpdateProps,onMounted  } from "@odoo/owl";
import { useComponent,useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const durationData = {
    'days': 'Days',
    'months': 'Months',
    'years': 'Years',
};

export class ExpiredLotsDashboardRenderer extends KanbanRenderer {
    setup() {
        super.setup();
        this.a_ids = [];
        this.b_ids = [];
        this.c_ids = [];
        this.d_ids = [];
        this.actionService = useService("action");
        this.orm = useService("orm");
        onMounted(() => {
            this.fetchExpiredProducts();
        });
    }


    async fetchExpiredProducts() {
        const data = await this.orm.call('stock.lot', 'get_expired_products', []);
        this.updateContent(data);
    }

    updateContent(data) {
        var blocks = ['a', 'b', 'c'];
        for(var block of blocks){
            var blockData = data[`block_${block}`];
            var $count = $(`.expired-lots-${block}-count`);
            var $duration = $(`.expired-lots-${block}-duration`);
            var $unit = $(`.expired-lots-${block}-unit`);
            $count.text(blockData.count);
            $count.closest('div').css('background', blockData.color);
            $duration.text(blockData.duration);
            $unit.text(durationData[blockData.unit]);
            this[`${block}_ids`] = blockData.ids;
        }
        var blockDData = data['block_d'];
        var $DCount = $('.expired-lots-d-count');
        $DCount.text(blockDData.count);
        $DCount.closest('div').css('background', blockDData.color);
        this.d_ids = blockDData.ids;
    }

    _onClickExpireLotsCard(event) {
        var $block = $(event.currentTarget);
        return this.actionService.doAction({
            name: "Lots",
            type: "ir.actions.act_window",
            res_model: "stock.lot",
            domain: [['id', 'in', this[`${$block.data().blockName}_ids`]]],
            views: [[false, "list"], [false, "form"]],
            view_mode: "list",
            target: "current"
        });

    }
}

ExpiredLotsDashboardRenderer.template = "noi_expired_lots.ExpiredLotsDashboard";
//ExpiredLotsDashboardRenderer.components = {
//    ...KanbanRenderer.components,
//};

export const ExpiredLotsKanbanView = {
    ...kanbanView,
//    Controller : KanbanController,
    Renderer: ExpiredLotsDashboardRenderer,
};


registry.category("views").add("noi_expired_lots", ExpiredLotsKanbanView);
