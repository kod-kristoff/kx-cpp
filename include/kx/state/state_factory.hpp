#ifndef KX_STATE_STATE_FACTORY_HPP
#define KX_STATE_STATE_FACTORY_HPP

#include "kx/state/state_fwd.hpp"

namespace kx::state
{
    class StateFactory
    {
    public:
        virtual ~StateFactory();
        virtual
        State * create_state(char const * name) = 0;
    };
}
#endif
