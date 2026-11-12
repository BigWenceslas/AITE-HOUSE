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
        minDate: String,
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.state = useState({ date: this.props.defaultDate, busy: false });
    }

    /** Une date (AAAA-MM-JJ) à partir d'aujourd'hui. */
    get isValid() {
        return Boolean(this.state.date) && this.state.date >= this.props.minDate;
    }

    async confirm() {
        if (this.state.busy || !this.isValid) {
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

/**
 * « Réassigner » : choix de la personne, puis confirmation explicite (la
 * personne est notifiée et devient abonnée de l'opportunité, ce qui ne
 * s'annule pas en réassignant de nouveau).
 */
export class AiteActivityReassignDialog extends Component {
    static template = "aite_crm_activity.ReassignDialog";
    static components = { Dialog };
    static props = {
        activity: Object,
        users: Array,
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.state = useState({ userId: "", busy: false });
    }

    get selectedUser() {
        const userId = parseInt(this.state.userId);
        return this.props.users.find((u) => u.id === userId);
    }

    async confirm() {
        const user = this.selectedUser;
        if (this.state.busy || !user) {
            return;
        }
        this.state.busy = true;
        try {
            await this.props.onConfirm(user);
            this.props.close();
        } finally {
            this.state.busy = false;
        }
    }
}
