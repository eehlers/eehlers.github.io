
extern crate bitcoin;
extern crate miniscript;

use std::str::FromStr;

fn main() {
    let desc = miniscript::Descriptor::<
        bitcoin::PublicKey,
    >::from_str("\
        sh(wsh(or_d(\
            c:pk(020e0338c96a8870479f2396c373cc7696ba124e8635d41b0ea581112b67817261),\
            c:pk(020e0338c96a8870479f2396c373cc7696ba124e8635d41b0ea581112b67817261)\
        )))\
    ").unwrap();

    // Derive the P2SH address
    assert_eq!(
        desc.address(bitcoin::Network::Bitcoin).unwrap().to_string(),
        "32aAVauGwencZwisuvd3anhhhQhNZQPyHv"
    );

    // Estimate the satisfaction cost
    assert_eq!(desc.max_satisfaction_weight(), 293);

    println!("{}", desc.script_pubkey());
    println!("{}", desc.witness_script());
    println!("{}", desc.address(bitcoin::Network::Bitcoin).unwrap().to_string());
}

