# -*- coding: utf-8 -*-
"""Modèle applatissant la réponse JSON de la route GCMS /statistics."""

# Correspondance identifiant client brut → libellé affiché.
CLIENT_LABELS = {
    "SIG-QGIS": "QGIS Plugin",
    "WEB": "Interface Web",
    "API": "API directe",
    "MOBILE": "Application Mobile",
}


class StatisticsData(object):
    """Vue applatie et prête à l'affichage des statistiques d'une base."""

    def __init__(self) -> None:
        self.start = u"–"
        self.end = u"–"
        self.inserts = 0
        self.updates = 0
        self.deletes = 0
        self.tx_total = 0
        self.tx_failed = 0
        self.tables = []       # list[str]
        self.clients = []      # list[(label, count)]
        self.users = []        # list[dict]
        self.has_aggregate = False

    @property
    def contrib_total(self) -> int:
        return self.inserts + self.updates + self.deletes

    @classmethod
    def fromPayload(cls, payload: dict) -> "StatisticsData":
        data = cls()
        if not isinstance(payload, dict):
            return data

        period = payload.get('period') or {}
        data.start = period.get('start') or u"–"
        data.end = period.get('end') or u"–"

        aggregate = payload.get('aggregate') if isinstance(payload.get('aggregate'), dict) else None
        data.has_aggregate = aggregate is not None
        source = aggregate if aggregate is not None else payload

        by_client = (source.get('contributions') or {}).get('by_client', {})
        data.inserts, data.updates, data.deletes = cls.__sumIUD(by_client)

        transactions = source.get('transactions') or {}
        data.tx_total = transactions.get('total', 0)
        data.tx_failed = transactions.get('failed', 0)
        data.tables = transactions.get('tables') or transactions.get('touched_tables') or []

        data.clients = cls.__clients(by_client)
        by_user = payload.get('by_user') if isinstance(payload.get('by_user'), list) else []
        data.users = cls.__users(by_user)
        return data

    @staticmethod
    def __sumIUD(by_client) -> tuple:
        inserts = updates = deletes = 0
        if isinstance(by_client, dict):
            counts_iter = by_client.values()
        elif isinstance(by_client, list):
            counts_iter = by_client
        else:
            counts_iter = []
        for counts in counts_iter:
            if isinstance(counts, dict):
                inserts += int(counts.get('Insert', 0) or 0)
                updates += int(counts.get('Update', 0) or 0)
                deletes += int(counts.get('Delete', 0) or 0)
        return inserts, updates, deletes

    @staticmethod
    def __clients(by_client) -> list:
        rows = []
        if isinstance(by_client, dict):
            for client, counts in by_client.items():
                total = 0
                if isinstance(counts, dict):
                    total = sum(int(counts.get(state, 0) or 0)
                                for state in ('Insert', 'Update', 'Delete'))
                rows.append((CLIENT_LABELS.get(client, client), total))
        elif isinstance(by_client, list):
            for entry in by_client:
                if not isinstance(entry, dict):
                    continue
                raw = (entry.get('client') or entry.get('client_device')
                       or entry.get('name') or str(entry))
                count = (entry.get('count') or entry.get('contributions')
                         or entry.get('total') or 0)
                rows.append((CLIENT_LABELS.get(raw, raw), count))
        rows.sort(key=lambda item: item[1], reverse=True)
        return rows

    @classmethod
    def __users(cls, by_user) -> list:
        users = []
        for entry in by_user:
            if not isinstance(entry, dict):
                continue
            username = (entry.get('user') or {}).get('username', u'?')
            by_client = (entry.get('contributions') or {}).get('by_client', {})
            inserts, updates, deletes = cls.__sumIUD(by_client)
            tx_total = (entry.get('transactions') or {}).get('total', 0)
            users.append({
                'username': username,
                'inserts': inserts,
                'updates': updates,
                'deletes': deletes,
                'tx_total': tx_total,
                'total': inserts + updates + deletes,
            })
        return users
