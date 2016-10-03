from datetime import datetime
from numpy import median, percentile
from sqlalchemy.orm import sessionmaker
from db import Base, Ignition, Virtualmachine, Processordata, Processoraggdata, Memorydata, Memoryaggdata, \
    Localdiskdata, Localdiskaggdata, Blockdiskdata, Blockdiskaggdata, Internalnetworkdata, Internalnetworkaggdata

# Bind Ignition to the metadata of the Base class
Base.metadata.bind = Ignition
Session = sessionmaker(bind=Ignition)


def log_error(e):
    err_msg = "%s:\n%s\n\n" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e)
    with open(log_file, "a") as log_handle:
        log_handle.write(err_msg)
    log_handle.close()
    print err_msg
    return


def generate_aggregates():
    session = Session()
    vms = session.query(Virtualmachine.id).all()

    for vm in vms:
        if processordata == "y":
            res = session.query(Processordata.vm_id, Processordata.os_id).filter(Processordata.vm_id == vm.id).first()
            if res:
                try:
                    OpenProcessoraggdata = Processoraggdata(
                            vm_id=res.vm_id,
                            os_id=res.os_id,
                            timestamp=timestamp
                    )
                    session.add(OpenProcessoraggdata)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    log_error(e)

                agg_id = OpenProcessoraggdata.id
                data_table = "xiaoice_processordata"
                agg_table = "xiaoice_processoraggdata"
                field = "performance"

                for term in term_list:
                    output = agg_data(term, data_table, field, res.vm_id)
                    if output:
                        try:
                            Ignition.execute("UPDATE %s SET %s_min = %s, %s_25 = %s, %s_75 = %s, %s_max = %s, %s_median = %s \
                                              WHERE id = %s" % (
                                agg_table, term, output['resultmin'], term, output['result25'],
                                term, output['result75'], term, output['resultmax'], term, output['resultmedian'],
                                agg_id))
                        except Exception as e:
                            session.rollback()
                            log_error(e)

        if memorydata == "y":
            res = session.query(Memorydata.vm_id, Memorydata.os_id).filter(Memorydata.vm_id == vm.id).first()
            if res:
                try:
                    OpenMemoryaggdata = Memoryaggdata(
                            vm_id=res.vm_id,
                            os_id=res.os_id,
                            timestamp=timestamp
                    )
                    session.add(OpenMemoryaggdata)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    log_error(e)

                agg_id = OpenMemoryaggdata.id
                data_table = "xiaoice_memorydata"
                agg_table = "xiaoice_memoryaggdata"
                field = "bandwidth"

                for term in term_list:
                    output = agg_data(term, data_table, field, res.vm_id)
                    if output:
                        try:
                            Ignition.execute("UPDATE %s SET %s_min = %s, %s_25 = %s, %s_75 = %s, %s_max = %s, %s_median = %s \
                                              WHERE id = %s" % (
                                agg_table, term, output['resultmin'], term, output['result25'],
                                term, output['result75'], term, output['resultmax'], term, output['resultmedian'],
                                agg_id))
                        except Exception as e:
                            session.rollback()
                            log_error(e)

        if localdiskdata == "y":
            res = session.query(Localdiskdata.vm_id, Localdiskdata.os_id).filter(Localdiskdata.vm_id == vm.id).first()
            if res:
                try:
                    OpenLocaldiskaggdata = Localdiskaggdata(
                            vm_id=res.vm_id,
                            os_id=res.os_id,
                            timestamp=timestamp
                    )
                    session.add(OpenLocaldiskaggdata)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    log_error(e)

                agg_id = OpenLocaldiskaggdata.id
                data_table = "xiaoice_localdiskdata"
                agg_table = "xiaoice_localdiskaggdata"

                fields = ['iops_read_seq',
                          'iops_write_seq',
                          'iops_read_random',
                          'iops_write_random',
                          'throughput_read_seq',
                          'throughput_write_seq',
                          'throughput_read_random',
                          'throughput_write_random',
                          'latency_read_seq',
                          'latency_write_seq',
                          'latency_read_random',
                          'latency_write_random']

                for field in fields:
                    for term in term_list:
                        output = agg_data(term, data_table, field, res.vm_id)
                        if output:
                            try:
                                Ignition.execute(
                                        "UPDATE %s SET %s_%s_min = %s, %s_%s_25 = %s, %s_%s_75 = %s, %s_%s_max = %s, %s_%s_median = %s WHERE id = %s" % (
                                            agg_table, field, term, output['resultmin'], field, term,
                                            output['result25'],
                                            field, term,
                                            output['result75'], field, term, output['resultmax'], field, term,
                                            output['resultmedian'], agg_id))

                            except Exception as e:
                                session.rollback()
                                log_error(e)

        if blockdiskdata == "y":
            res = session.query(Blockdiskdata.vm_id, Blockdiskdata.os_id, Blockdiskdata.disk_size_id).filter(
                    Blockdiskdata.vm_id == vm.id).first()
            if res:
                try:
                    OpenBlockdiskaggdata = Blockdiskaggdata(
                            vm_id=res.vm_id,
                            os_id=res.os_id,
                            disk_size_id=res.disk_size_id,
                            timestamp=timestamp
                    )
                    session.add(OpenBlockdiskaggdata)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    log_error(e)

                agg_id = OpenLocaldiskaggdata.id
                data_table = "xiaoice_blockdiskdata"
                agg_table = "xiaoice_blockdiskaggdata"

                fields = ['iops_read_seq',
                          'iops_write_seq',
                          'iops_read_random',
                          'iops_write_random',
                          'throughput_read_seq',
                          'throughput_write_seq',
                          'throughput_read_random',
                          'throughput_write_random',
                          'latency_read_seq',
                          'latency_write_seq',
                          'latency_read_random',
                          'latency_write_random']

                for field in fields:
                    for term in term_list:
                        output = agg_data(term, data_table, field, res.vm_id)
                        if output:
                            try:
                                Ignition.execute(
                                        "UPDATE %s SET %s_%s_min = %s, %s_%s_25 = %s, %s_%s_75 = %s, %s_%s_max = %s, %s_%s_median = %s WHERE id = %s" % (
                                            agg_table, field, term, output['resultmin'], field, term,
                                            output['result25'],
                                            field, term,
                                            output['result75'], field, term, output['resultmax'], field, term,
                                            output['resultmedian'], agg_id))

                            except Exception as e:
                                session.rollback()
                                log_error(e)

        if internalnetworkdata == "y":
            res = session.query(Internalnetworkdata.vm_id, Internalnetworkdata.os_id).filter(
                    Internalnetworkdata.vm_id == vm.id).first()
            if res:
                try:
                    OpenInternalnetworkaggdata = Internalnetworkaggdata(
                            vm_id=res.vm_id,
                            os_id=res.os_id,
                            timestamp=timestamp
                    )
                    session.add(OpenInternalnetworkaggdata)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    log_error(e)

                agg_id = OpenProcessoraggdata.id
                data_table = "xiaoice_internalnetworkdata"
                agg_table = "xiaoice_internalnetworkaggdata"
                fields = ['single_threaded_throughput', 'multi_threaded_throughput']

                for field in fields:
                    for term in term_list:
                        output = agg_data(term, data_table, field, res.vm_id)
                        if output:
                            try:
                                Ignition.execute(
                                        "UPDATE %s SET %s_%s_min = %s, %s_%s_25 = %s, %s_%s_75 = %s, %s_%s_max = %s, %s_%s_median = %s WHERE id = %s" % (
                                            agg_table, field, term, output['resultmin'], field, term,
                                            output['result25'],
                                            field, term,
                                            output['result75'], field, term, output['resultmax'], field, term,
                                            output['resultmedian'], agg_id))

                            except Exception as e:
                                session.rollback()
                                log_error(e)
    session.close()


def agg_data(term, table, field, vm_id):
    try:
        # Fetches aggregate data for the previous month
        if term is 'month':
            results = Ignition.execute(
                    "SELECT %s FROM %s WHERE YEAR(timestamp) = YEAR(CURDATE() - INTERVAL 1 MONTH) AND MONTH(timestamp) = MONTH(CURDATE() - INTERVAL 1 MONTH) AND vm_id = %s" % (
                        field, table, vm_id))
        # Fetches aggregate data from one year back to current date
        elif term is 'year':
            results = Ignition.execute(
                    "SELECT %s FROM %s WHERE timestamp BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE() AND vm_id = %s" % (
                        field, table, vm_id))
        # Fetches aggregate data from the beginning to current date
        elif term is 'lifetime':
            results = Ignition.execute("SELECT %s FROM %s WHERE vm_id = %s" % (field, table, vm_id))
    except Exception as e:
        log_error(e)

    results = [d[field] for d in results if field in d]
    results = filter(lambda x: x is not None, results)
    output = {}
    if results:
        try:
            output['resultmin'] = min(results)
            output['result25'] = percentile(results, 25)
            output['resultmedian'] = median(results)
            output['result75'] = percentile(results, 75)
            output['resultmax'] = max(results)
            print "\n===== Table: %s ===== Field: %s ===== Term: %s =====\n" % (table, field, term)
            print "min,25th,median,75th,max"
            print "%s,%s,%s,%s,%s" % (
                output['resultmin'], output['result25'], output['resultmedian'], output['result75'],
                output['resultmax'])
        except Exception as e:
            log_error(e)
        return output


# Enable / disable aggregate data collection
processordata = "y"
memorydata = "y"
localdiskdata = "y"
blockdiskdata = "y"
internalnetworkdata = "y"
log_file = "hera.log"
term_list = ['month', 'year', 'lifetime']
timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
generate_aggregates()
