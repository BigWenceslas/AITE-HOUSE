/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import {
    getQuickPeriods, HOUR_PRESETS, WEEKDAYS, WEEKDAY_PRESETS,
} from "../services/utils";

/**
 * Barre de filtre enrichie.
 *
 * Émet ``onChange(payload)`` au parent avec :
 *   - key         : clé de période rapide ("month", "custom", …)
 *   - from / to   : bornes de date ISO (YYYY-MM-DD)
 *   - configId    : caisse sélectionnée (int) ou null = toutes
 *   - hourKey     : clé de plage horaire ("all", "evening", "custom"…)
 *   - hourFrom    : heure début [0-23] ou null
 *   - hourTo      : heure fin [0-23] (incluse) ou null
 *   - weekdayKey  : clé de filtre jour ("all", "week", "weekend", "manual")
 *   - weekdays    : liste ISO 1=lundi … 7=dimanche (vide = tous)
 *
 * Le parent reste la source de vérité ; ce composant ne stocke que les
 * champs de saisie libre (dates et heures custom).
 */
export class FilterBar extends Component {
    static template = "aite_pos_analytics.FilterBar";
    static props = {
        currentKey: String,
        dateFrom: { type: [String, { value: null }] },
        dateTo: { type: [String, { value: null }] },
        configs: Array,
        configId: { type: [Number, { value: null }] },
        onChange: Function,
        minDate: { type: [String, { value: null }], optional: true },
        maxDate: { type: [String, { value: null }], optional: true },
        // Filtres temporels (pilotés par le parent)
        hourKey: { type: String, optional: true },
        hourFrom: { type: [Number, { value: null }], optional: true },
        hourTo: { type: [Number, { value: null }], optional: true },
        weekdayKey: { type: String, optional: true },
        weekdays: { type: Array, optional: true },
    };

    setup() {
        this.periods = getQuickPeriods();
        this.hourPresets = HOUR_PRESETS;
        this.weekdays = WEEKDAYS;
        this.state = useState({
            customFrom: this.props.dateFrom || "",
            customTo: this.props.dateTo || "",
            // Heures custom : on initialise depuis les props si fournies
            customHourFrom: this.props.hourFrom != null ? this.props.hourFrom : 18,
            customHourTo: this.props.hourTo != null ? this.props.hourTo : 23,
        });
    }

    // ---- payload courant (factorise la lecture des props) ----
    _payload(overrides = {}) {
        return {
            key: this.props.currentKey,
            from: this.props.dateFrom,
            to: this.props.dateTo,
            configId: this.props.configId,
            hourKey: this.props.hourKey || "all",
            hourFrom: this.props.hourFrom ?? null,
            hourTo: this.props.hourTo ?? null,
            weekdayKey: this.props.weekdayKey || "all",
            weekdays: this.props.weekdays || [],
            ...overrides,
        };
    }

    // ================= PÉRIODE =================
    onQuickClick(ev) {
        const key = ev.currentTarget.dataset.periodKey;
        if (key) this.selectQuick(key);
    }

    selectQuick(key) {
        const p = this.periods[key];
        if (!p) return;
        const from = p.from || this.props.minDate;
        const to = p.to || this.props.maxDate;
        this.state.customFrom = from || "";
        this.state.customTo = to || "";
        this.props.onChange(this._payload({ key, from, to }));
    }

    applyCustom() {
        const { customFrom, customTo } = this.state;
        if (!customFrom || !customTo) return;
        if (new Date(customFrom) > new Date(customTo)) return;
        this.props.onChange(this._payload({
            key: "custom", from: customFrom, to: customTo,
        }));
    }

    // ================= CAISSE =================
    onConfigClick(ev) {
        const raw = ev.currentTarget.dataset.configId;
        const configId = raw === "all" ? null : parseInt(raw, 10);
        this.props.onChange(this._payload({ configId }));
    }

    // garde le <select> de repli (mobile / nombreuses caisses)
    onConfigChange(ev) {
        const v = ev.target.value;
        const configId = v ? parseInt(v, 10) : null;
        this.props.onChange(this._payload({ configId }));
    }

    // ================= HEURE =================
    onHourPreset(ev) {
        const key = ev.currentTarget.dataset.hourKey;
        const preset = this.hourPresets[key];
        if (!preset) return;
        this.props.onChange(this._payload({
            hourKey: key, hourFrom: preset.from, hourTo: preset.to,
        }));
    }

    applyCustomHour() {
        let f = parseInt(this.state.customHourFrom, 10);
        let t = parseInt(this.state.customHourTo, 10);
        if (isNaN(f) || isNaN(t)) return;
        f = Math.max(0, Math.min(23, f));
        t = Math.max(0, Math.min(23, t));
        this.props.onChange(this._payload({
            hourKey: "custom", hourFrom: f, hourTo: t,
        }));
    }

    // ================= JOUR DE SEMAINE =================
    onWeekdayPreset(ev) {
        const key = ev.currentTarget.dataset.weekdayKey;
        const list = WEEKDAY_PRESETS[key] || [];
        this.props.onChange(this._payload({
            weekdayKey: key, weekdays: [...list],
        }));
    }

    /** Toggle d'un jour individuel : bascule en mode "manual". */
    toggleWeekday(ev) {
        const day = parseInt(ev.currentTarget.dataset.weekday, 10);
        if (isNaN(day)) return;
        const current = new Set(this.props.weekdays || []);
        if (current.has(day)) {
            current.delete(day);
        } else {
            current.add(day);
        }
        const list = [...current].sort((a, b) => a - b);
        this.props.onChange(this._payload({
            weekdayKey: list.length ? "manual" : "all",
            weekdays: list,
        }));
    }

    // ---- helpers de rendu ----
    isWeekdayActive(day) {
        return (this.props.weekdays || []).includes(day);
    }
    isAllDays() {
        return !(this.props.weekdays && this.props.weekdays.length);
    }
}
