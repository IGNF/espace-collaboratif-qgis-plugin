# -*- coding: utf-8 -*-
"""Modèle applatissant la réponse JSON de la route GCMS /statistics."""

# Correspondance identifiant client brut → libellé affiché.
CLIENT_LABELS = {
    "SIG-QGIS": "QGIS",
    "WEB": "Interface Web",
    "API": "API directe",
    "MOBILE": "Mobile",
}
UNKNOWN_CLIENT_LABEL = u"Non identifié"
UNKNOWN_CLIENT_VALUES = {u"", u"unknown", u"unknow", u"inconnu", u"non identifié",
                         u"non identifie", u"null", u"none"}


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

    @property
    def has_statistics(self) -> bool:
        """Indique si au moins un indicateur ou détail contient une donnée utile."""
        return any((
            self.contrib_total,
            self.tx_total,
            self.tx_failed,
            self.tables,
            any(count for _, count in self.clients),
            any(user['total'] or user['tx_total'] for user in self.users),
        ))

    @classmethod
    def fromPayload(cls, payload: dict) -> "StatisticsData":
        """Convertit la réponse API en données consommées par le dialogue.

        "clients" contient des couples libellé/nombre pour le graphique
        horizontal; "users" contient les comptes par utilisateur pour le
        tableau classé et le filtre administrateur. Les totaux de contributions
        et de transactions alimentent les cartes et le graphique de répartition.
        Une réponse de premier niveau invalide renvoie les valeurs par défaut.
        """
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
        """Renvoie les couples libellé/nombre client, triés par nombre décroissant."""
        rows = []
        if isinstance(by_client, dict):
            for client, counts in by_client.items():
                total = 0
                if isinstance(counts, dict):
                    total = sum(int(counts.get(state, 0) or 0)
                                for state in ('Insert', 'Update', 'Delete'))
                rows.append((StatisticsData.__clientLabel(client), total))
        elif isinstance(by_client, list):
            for entry in by_client:
                if not isinstance(entry, dict):
                    continue
                raw = entry.get('client') or entry.get('client_device') or entry.get('name')
                count = (entry.get('count') or entry.get('contributions')
                         or entry.get('total') or 0)
                rows.append((StatisticsData.__clientLabel(raw), int(count or 0)))
        rows.sort(key=lambda item: item[1], reverse=True)
        return rows

    @staticmethod
    def __clientLabel(client) -> str:
        if client is None or str(client).strip().lower() in UNKNOWN_CLIENT_VALUES:
            return UNKNOWN_CLIENT_LABEL
        return CLIENT_LABELS.get(client, str(client))

    @classmethod
    def __users(cls, by_user) -> list:
        """Renvoie les utilisateurs avec identifiant, nom et totaux par opération."""
        users = []
        for entry in by_user:
            if not isinstance(entry, dict):
                continue
            user = entry.get('user') or {}
            if not isinstance(user, dict):
                user = {}
            username = user.get('username') or entry.get('username') or u'?'
            user_id = user.get('id')
            if user_id is None:
                user_id = user.get('user_id')
            if user_id is None:
                user_id = entry.get('user_id', entry.get('userId'))
            by_client = (entry.get('contributions') or {}).get('by_client', {})
            inserts, updates, deletes = cls.__sumIUD(by_client)
            tx_total = (entry.get('transactions') or {}).get('total', 0)
            users.append({
                'user_id': user_id,
                'username': username,
                'inserts': inserts,
                'updates': updates,
                'deletes': deletes,
                'tx_total': tx_total,
                'total': inserts + updates + deletes,
            })
        return users
