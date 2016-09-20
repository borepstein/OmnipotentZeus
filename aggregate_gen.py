import pymysql
from numpy import median, percentile


class AggregateGenerator:

    def __init__(self):
        # Database credentials
        self.host = "192.168.20.42"
        self.user = "root"
        self.password = "inapp"
        self.db = "perf_forecast"
        self.term_list = ['month', 'year', 'lifetime']

        # Enable / disable aggregate data collection
        self.processordata = "y"
        self.memorydata = "y"
        self.localdiskdata = "y"
        self.blockdiskdata = "y"
        self.internalnetworkdata = "y"

        self.cur = self.db_connection(self.host, self.user, self.password, self.db)

    def db_connection(self, host, user, password, db):
        self.con = pymysql.connect(host, user, password, db)
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        return cur

    def generate_aggregates(self):

        self.cur.execute("SELECT id from xiaoice_virtualmachine")
        results = self.cur.fetchall()

        for result in results:
            if self.processordata == "y":
                table = "xiaoice_processordata"
                field = "performance"

                try:
                    self.cur.execute("SELECT vm_id, cores_id, os_id FROM %s WHERE vm_id = %s" % (table, result['id']))
                    res = self.cur.fetchone()

                    self.cur.execute("INSERT INTO xiaoice_processoraggdata (vm_id, cores_id, os_id) VALUES (%s, %s, %s)" % (res['vm_id'], res['cores_id'], res['os_id']))
                    self.con.commit()
                    agg_id = self.cur.lastrowid

                    for term in self.term_list:
                        output = self.agg_data(term, table, field, res['vm_id'])
                        if output:
                            self.cur.execute("UPDATE xiaoice_processoraggdata SET %s_min = %s, %s_25 = %s, %s_75 = %s, %s_max = %s, %s_median = %s WHERE id = %s" % (term, output['resultmin'], term, output['result25'], term, output['result75'], term, output['resultmax'], term, output['resultmedian'], agg_id))
                            self.con.commit()
                except Exception as e:
                    pass

            if self.memorydata == "y":
                table = "xiaoice_memorydata"
                field = "bandwidth"

                try:
                    self.cur.execute("SELECT vm_id, cores_id, os_id FROM %s WHERE vm_id = %s" % (table, result['id']))
                    res = self.cur.fetchone()

                    self.cur.execute("INSERT INTO xiaoice_memoryaggdata (vm_id, cores_id, os_id) VALUES (%s, %s, %s)" % (res['vm_id'], res['cores_id'], res['os_id']))
                    self.con.commit()
                    agg_id = self.cur.lastrowid

                    for term in self.term_list:
                        output = self.agg_data(term, table, field, res['vm_id'])
                        if output:
                            self.cur.execute("UPDATE xiaoice_memoryaggdata SET %s_min = %s, %s_25 = %s, %s_75 = %s, %s_max = %s, %s_median = %s WHERE id = %s" % (term, output['resultmin'], term, output['result25'], term, output['result75'], term, output['resultmax'], term, output['resultmedian'], agg_id))
                            self.con.commit()
                except Exception as e:
                    pass

            if self.localdiskdata == "y":
                table = "xiaoice_localdiskdata"
                fields = ['iops_read_seq', 'iops_write_seq', 'iops_read_rand', 'iops_write_rand']

                try:
                    self.cur.execute("SELECT vm_id, cores_id, os_id FROM %s WHERE vm_id = %s" % (table, result['id']))
                    res = self.cur.fetchone()

                    self.cur.execute("INSERT INTO xiaoice_localdiskaggdata (vm_id, cores_id, os_id) VALUES (%s, %s, %s)" % (res['vm_id'], res['cores_id'], res['os_id']))
                    self.con.commit()
                    agg_id = self.cur.lastrowid

                    for field in fields:
                        for term in self.term_list:
                            output = self.agg_data(term, table, field, res['vm_id'])
                            if output:
                                self.cur.execute("UPDATE xiaoice_localdiskaggdata SET %s_%s_min = %s, %s_%s_25 = %s, %s_%s_75 = %s, %s_%s_max = %s, %s_%s_median = %s WHERE id = %s" % (field, term, output['resultmin'], field, term, output['result25'], field, term, output['result75'], field, term, output['resultmax'], field, term, output['resultmedian'], agg_id))
                                self.con.commit()
                except Exception as e:
                    pass

            if self.blockdiskdata == "y":
                table = "xiaoice_blockdiskdata"
                fields = ['iops_read_seq', 'iops_write_seq', 'iops_read_rand', 'iops_write_rand']

                try:
                    self.cur.execute("SELECT vm_id, cores_id, os_id FROM %s WHERE vm_id = %s" % (table, result['id']))
                    res = self.cur.fetchone()

                    self.cur.execute("INSERT INTO xiaoice_blockdiskaggdata (vm_id, cores_id, os_id) VALUES (%s, %s, %s)" % (res['vm_id'], res['cores_id'], res['os_id']))
                    self.con.commit()
                    agg_id = self.cur.lastrowid

                    for field in fields:
                        for term in self.term_list:
                            output = self.agg_data(term, table, field, res['vm_id'])
                            if output:
                                self.cur.execute("UPDATE xiaoice_blockdiskaggdata SET %s_%s_min = %s, %s_%s_25 = %s, %s_%s_75 = %s, %s_%s_max = %s, %s_%s_median = %s WHERE id = %s" % (field, term, output['resultmin'], field, term, output['result25'], field, term, output['result75'], field, term, output['resultmax'], field, term, output['resultmedian'], agg_id))
                                self.con.commit()
                except Exception as e:
                    pass

            if self.internalnetworkdata == "y":
                table = "xiaoice_internalnetworkdata"
                fields = ['single_threaded_throughput', 'multi_threaded_throughput']

                try:
                    self.cur.execute("SELECT vm_id, cores_id, os_id FROM %s WHERE vm_id = %s" % (table, result['id']))
                    res = self.cur.fetchone()

                    self.cur.execute("INSERT INTO xiaoice_internalnetworkaggdata (vm_id, cores_id, os_id) VALUES (%s, %s, %s)" % (res['vm_id'], res['cores_id'], res['os_id']))
                    self.con.commit()
                    agg_id = self.cur.lastrowid

                    for field in fields:
                        for term in self.term_list:
                            output = self.agg_data(term, table, field, res['vm_id'])
                            if output:
                                self.cur.execute("UPDATE xiaoice_internalnetworkaggdata SET %s_%s_min = %s, %s_%s_25 = %s, %s_%s_75 = %s, %s_%s_max = %s, %s_%s_median = %s WHERE id = %s" % (field, term, output['resultmin'], field, term, output['result25'], field, term, output['result75'], field, term, output['resultmax'], field, term, output['resultmedian'], agg_id))
                                self.con.commit()
                except Exception as e:
                    pass

    def agg_data(self, term, table, field, vm_id):

        try:
            # Fetches aggregate data for the previous month
            if term is 'month':
                self.cur.execute("SELECT %s FROM %s WHERE YEAR(timestamp) = YEAR(CURDATE() - INTERVAL 1 MONTH) AND MONTH(timestamp) = MONTH(CURDATE() - INTERVAL 1 MONTH) AND vm_id = %s" % (field, table, vm_id))
            # Fetches aggregate data from one year back to current date
            elif term is 'year':
                self.cur.execute("SELECT %s FROM %s WHERE timestamp BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE() AND vm_id = %s" % (field, table, vm_id))
            # Fetches aggregate data from the beginning to current date
            elif term is 'lifetime':
                self.cur.execute("SELECT %s FROM %s WHERE vm_id = %s" % (field, table, vm_id))
        except Exception as e:
            pass

        results = self.cur.fetchall()
        results = [d[field] for d in results if field in d]

        output = {}
        if results:
            output['resultmin'] = min(results)
            output['result25'] = percentile(results, 25)
            output['resultmedian'] = median(results)
            output['result75'] = percentile(results, 75)
            output['resultmax'] = max(results)
            print "\n===== Table: %s ===== Field: %s ===== Term: %s =====\n" % (table, field, term)
            print "min,25th,median,75th,max"
            print "%s,%s,%s,%s,%s" % (output['resultmin'], output['result25'], output['resultmedian'], output['result75'], output['resultmax'])
        return output

agg = AggregateGenerator()
agg.generate_aggregates()
