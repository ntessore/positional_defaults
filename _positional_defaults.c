// author: Nicolas Tessore <n.tessore@ucl.ac.uk>
// license: MIT

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>


typedef struct {
    PyObject_HEAD
    PyObject* dict;
    int number;
    PyObject* wrapped;
    PyObject* patterns;
    PyObject* placeholder;
} WrapObject;



static void
wrap_dealloc(WrapObject* self)
{
    Py_XDECREF(self->wrapped);
    Py_XDECREF(self->patterns);
    Py_XDECREF(self->placeholder);
    Py_TYPE(self)->tp_free((PyObject*)self);
}


static PyObject*
wrap_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    WrapObject* self = (WrapObject*)type->tp_alloc(type, 0);

    if (self != NULL) {
        self->number = 0;

        self->patterns = PyTuple_New(0);
        if (self->patterns == NULL) {
            Py_DECREF(self);
            return NULL;
        }

        Py_INCREF(Py_None);
        self->wrapped = Py_None;

        Py_INCREF(Py_None);
        self->placeholder = Py_None;
    }

    return (PyObject*)self;
}


static int
wrap_init(WrapObject* self, PyObject* args, PyObject* kwds)
{
    static char *kwlist[] = {"wrapped", "patterns", "placeholder", NULL};
    Py_ssize_t i, n;
    PyObject* wrapped, *patterns, *placeholder, *tmp;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOO:wrap", kwlist,
                                     &wrapped, &patterns, &placeholder))
        return -1;

    if (!PyTuple_Check(patterns)) {
        PyErr_SetString(PyExc_TypeError, "patterns must be tuple");
        return -1;
    }

    n = PyTuple_GET_SIZE(patterns);

    for (i = 0; i < n; ++i) {
        Py_ssize_t k, j, nargs;
        PyObject* pattern = PyTuple_GET_ITEM(patterns, i);
        if (!PyTuple_Check(pattern)) {
            PyErr_Format(PyExc_TypeError, "patterns[%zd] must be tuple", i);
            return -1;
        }
        nargs = 0;
        for (j = 0, k = PyTuple_GET_SIZE(pattern); j < k; ++j) {
            PyObject* item = PyTuple_GET_ITEM(pattern, j);
            if (item == placeholder)
                nargs += 1;
        }
        if (nargs != i) {
            PyErr_Format(PyExc_ValueError, "patterns[%zd] must contain "
                         "placeholder %zd times (found %zd)", i, i, nargs);
            return -1;
        }
    }

    self->number = n - 1;

    tmp = self->wrapped;
    Py_INCREF(wrapped);
    self->wrapped = wrapped;
    Py_XDECREF(tmp);

    tmp = self->patterns;
    Py_INCREF(patterns);
    self->patterns = patterns;
    Py_XDECREF(tmp);

    tmp = self->placeholder;
    Py_INCREF(placeholder);
    self->placeholder = placeholder;
    Py_XDECREF(tmp);

    return 0;
}


static PyMemberDef wrap_members[] = {
    {"__dict__", T_OBJECT, offsetof(WrapObject, dict), READONLY},
    {"wrapped", T_OBJECT, offsetof(WrapObject, wrapped), READONLY},
    {"patterns", T_OBJECT, offsetof(WrapObject, patterns), READONLY},
    {"placeholder", T_OBJECT, offsetof(WrapObject, placeholder), READONLY},
    {NULL}
};


static PyObject*
wrap_call(WrapObject* self, PyObject* args, PyObject* kwds) {
    Py_ssize_t n, k, i, j;
    PyObject *pattern, *newargs, *result;

    if (self->wrapped == NULL)
        Py_RETURN_NONE;

    n = PyTuple_GET_SIZE(args);

    if (n > self->number)
        return PyObject_Call(self->wrapped, args, kwds);

    pattern = PyTuple_GET_ITEM(self->patterns, n);
    k = PyTuple_GET_SIZE(pattern);

    newargs = PyTuple_New(k);
    if (newargs == NULL)
        return NULL;

    for (i = 0, j = 0; i < k; ++i) {
        PyObject* item = PyTuple_GET_ITEM(pattern, i);
        if (item == self->placeholder)
            item = PyTuple_GET_ITEM(args, j++);
        Py_INCREF(item);
        PyTuple_SET_ITEM(newargs, i, item);
    }

    result = PyObject_Call(self->wrapped, newargs, kwds);

    Py_DECREF(newargs);

    return result;
}


static PyObject*
wrap_get(PyObject* self, PyObject* obj, PyObject* type) {
    if (obj == Py_None || obj == NULL) {
        Py_INCREF(self);
        return self;
    }
    return PyMethod_New(self, obj);
}


static PyTypeObject WrapType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_positional_defaults.wrap",
    .tp_doc = PyDoc_STR("Wrapper that applies positional defaults."),
    .tp_basicsize = sizeof(WrapObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_dictoffset = offsetof(WrapObject, dict),
    .tp_new = wrap_new,
    .tp_init = (initproc)wrap_init,
    .tp_dealloc = (destructor)wrap_dealloc,
    .tp_members = wrap_members,
    .tp_call = (ternaryfunc)wrap_call,
    .tp_descr_get = wrap_get,
};


static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_positional_defaults",
    .m_doc = PyDoc_STR("Implementation of the positional_defaults package."),
    .m_size = -1,
};


PyMODINIT_FUNC
PyInit__positional_defaults(void) {
    PyObject* m;

    if (PyType_Ready(&WrapType) < 0)
        return NULL;

    m = PyModule_Create(&module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&WrapType);
    if (PyModule_AddObject(m, "wrap", (PyObject*)&WrapType) < 0) {
        Py_DECREF(&WrapType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
