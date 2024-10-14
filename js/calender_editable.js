/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CalendarCommonPopover } from "@web/views/calendar/calendar_common/calendar_common_popover";

patch(CalendarCommonPopover.prototype, {
    /**
     * Customising meal calendar
     *
     * @private
     * @override
     */
    onEditEvent() {
        this.props.model.fieldsMode = 'edit';
        this.props.editRecord(this.props.record);
        this.props.close();
    },
});