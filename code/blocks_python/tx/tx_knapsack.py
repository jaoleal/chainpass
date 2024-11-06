def tx_KISS(tx_list, remaining_size):
    #sort the list by fee/size ratio
    sorted_tx_list = sorted(tx_list, key=lambda x: x[0]/x[1], reverse=True)
    used_size = int()
    fee = int()
    used_tx_id = list()
    for i in range(len(sorted_tx_list)):
        if used_size + sorted_tx_list[i][1] <= remaining_size:
            used_size += sorted_tx_list[i][1]
            fee += sorted_tx_list[i][0]
            tx_id = sorted_tx_list[i][2].replace(".json", "")
            used_tx_id.insert(len(used_tx_id),tx_id)
        else:
            break
    #i have to keep track in the used txs, so i can include 
    # them on the block.

    return used_tx_id, fee