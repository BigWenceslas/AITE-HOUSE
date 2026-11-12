import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

/**
 * « Marquer comme fait » : compte rendu facultatif, publié dans
 * l'historique de l'opportunité.
 */
export class AiteActivityDoneDialog extends Component {
    static template = "aite_crm_activity.DoneDialog";
    static components = { Dialog };
    static props = {
        activity: Object,
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.state = useState({ feedback: "", busy: false });
    }

    async confirm() {
        if (this.state.busy) {
            return;
        }
        this.state.busy = true;
        try {
            await this.props.onConfirm(this.state.feedback);
            this.props.close();
        } finally {
            this.state.busy = false;
        }
    }
}

/**
 * « Reporter à une date » : choix libre de la nouvelle échéance.
 */
export class AiteActivityDateDialog extends Component {
    static template = "aite_crm_activity.DateDialog";
    static components = { Dialog };
    static props = {
        activity: Object,
        defaultDate: String,
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.state = useState({ date: this.props.defaultDate, busy: false });
    }

    async confirm() {
        if (this.state.busy || !this.state.date) {
            return;
        }
        this.state.busy = true;
        try {
            await this.props.onConfirm(this.state.date);
            this.props.close();
        } finally {
            this.state.busy = false;
        }
    }
}
